# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio.h

Purpose: public internal header for DPIO MC object control APIs and DPIO attribute/config types.

Important APIs/types: declares MC command wrappers from `dpio.c`; defines `enum dpio_channel_mode`, `struct dpio_cfg`, and `struct dpio_attr`. Attribute fields describe object ID, software portal CE/CI offsets, portal ID, notification mode/priorities, QBMan version, and clock frequency.

Control flow and integration: `dpio-driver.c` uses this header to open, reset, enable, inspect, and disable DPIO objects before creating a `dpaa2_io` service.

State and persistence: no state. Structs carry MC firmware state into driver setup.

Dependencies and risks: depends on `struct fsl_mc_io` from the MC bus. Risks are type drift with MC response structures and callers assuming notification priorities imply a valid local channel.

Test signals: build coverage for DPIO driver, valid decoded attributes during probe, and compile-time consistency with `dpio-cmd.h`.
