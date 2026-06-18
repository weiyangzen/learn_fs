# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-fw-com.h

## Purpose
This header exposes the generic firmware communication configuration and token-queue API used by IPU6 subsystem-specific firmware layers.

## Important APIs, types, and functions
`struct ipu6_fw_syscom_queue_config` describes token count and token size. `struct ipu6_fw_com_cfg` supplies queue arrays, queue counts, DMEM address, firmware-specific configuration blob, callback hooks, and buttress boot-parameter offset. Public functions prepare, open, check readiness, close, release, and get/put send/receive tokens. `SYSCOM_BUTTRESS_FW_PARAMS_ISYS_OFFSET` identifies the ISYS boot-parameter area.

## Control flow and integration points
ISYS fills this config in `ipu6-fw-isys.c`, then uses the returned opaque `ipu6_fw_com_context` for all firmware command and response queues. The opaque context keeps the header independent of queue memory layout internals.

## State, persistence, and dependencies
The header stores no state. The config's callback pointers are critical because fw-com does not know how to start or query each subsystem cell. Dependencies are minimal forward declarations for `ipu6_fw_com_context` and `ipu6_bus_device`.

## Risks and test signals
Risks are invalid queue counts/sizes, missing callbacks, wrong DMEM or boot-parameter offset, and callers using token pointers after release. Test signals include build coverage for consumers, ISYS firmware open/close, queue full handling, and command/response traffic across all configured queues.
