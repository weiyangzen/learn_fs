# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-indices.c

## Purpose
Implements `/dev/papr-indices`, exposing PAPR sensor/indicator index retrieval and dynamic sensor/indicator get/set operations to userspace.

## Important APIs, Types, And Functions
The sequence retrieval path uses `struct rtas_get_indices_params`, `rtas_ibm_get_indices`, `indices_sequence_begin`, `indices_sequence_end`, `indices_sequence_fill_work_area`, `papr_indices_create_handle`, and `papr_indices_handle_read`. Dynamic operations use `papr_dynamic_indice_buf_from_user`, `papr_dynamic_indicator_ioc_set`, and `papr_dynamic_sensor_ioc_get`. The miscdevice ioctl dispatcher is `papr_indices_dev_ioctl`.

## Control Flow
For `PAPR_INDICES_IOC_GET`, user input selects sensor versus indicator and type. The code builds a `papr_rtas_sequence`, serializes the RTAS sequence under `rtas_ibm_get_indices_lock`, accumulates complete fixed-size work-area pages through common PAPR blob helpers, and returns an anonymous fd for read/seek/release. Dynamic sensor and indicator ioctls copy a location-code block from user space, validate NULL termination, build an RTAS work area, issue the appropriate RTAS call under its function lock, and return or store state.

## State And Persistence
The indices retrieval result is immutable blob data attached to an anonymous file until release. Dynamic indicator sets persist in platform firmware/device state. There is no kernel durable storage.

## Dependencies And Integration Points
Depends on RTAS work areas and function locks, PAPR common sequence helpers, miscdevice/ioctl/uaccess, uapi `papr-indices` structures, and PAPR RTAS functions `ibm,get-indices`, `ibm,set-dynamic-indicator`, and `ibm,get-dynamic-sensor-state`.

## Risks And Edge Cases
`ibm,get-indices` does not report bytes written, so each successful call appends the full fixed work-area size and read requires at least that size. RTAS `RTAS_SEQ_START_OVER` maps to `-EAGAIN` and is retried by common sequence code. Location-code strings must be terminated and length includes the NULL. Indicator/sensor absence maps to `-EOPNOTSUPP`.

## Test Signals
Test device registration with missing and present RTAS tokens, sequence retry on start-over, multi-buffer reads and llseek, too-small read buffers, malformed location strings, dynamic sensor get, dynamic indicator set with read-only fd rejection, and RTAS hardware/parameter errors.
