<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_tool.h -->
# sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_tool.h

## Purpose

`mpi_tool.h` defines MPI toolbox and diagnostic message layouts: clean persistent regions, memory move, diagnostic data upload, ISTWI read/write, FC management, beacon control, diagnostic buffer post, and diagnostic release. These are management and service operations around the normal IO path.

## Important APIs, Types, and Definitions

- Toolbox selectors identify clean, memory move, diagnostic upload, ISTWI read/write, FC management, and beacon tools.
- `MSG_TOOLBOX_REPLY` is the common toolbox completion with tool, message length, function, context, IOC status, and IOC log info.
- `MSG_TOOLBOX_CLEAN_REQUEST` selects persistent regions such as NVSRAM, SEEPROM, flash, bootloader, firmware backup/current, other persistent pages, manufacturing pages, and boot services.
- `MSG_TOOLBOX_MEM_MOVE_REQUEST` and `MSG_TOOLBOX_DIAG_DATA_UPLOAD_REQUEST` use SGEs for firmware-directed memory movement or diagnostic upload. `DIAG_DATA_UPLOAD_HEADER` describes upload length and format.
- `MSG_TOOLBOX_ISTWI_READ_WRITE_REQUEST` performs I2C-like ISTWI reads/writes with bus number, device address, up to three address bytes, data length, direction flag, and SGE.
- FC management action info unions support discovery by all ports, port identifier, bus/target ID, and max frame size.
- `MSG_TOOLBOX_BEACON_REQUEST` toggles beacon mode for a connector/port.
- `MSG_DIAG_BUFFER_POST_REQUEST` posts trace/snapshot/extended diagnostic buffers by type, length, product-specific fields, extended type, and 64-bit buffer address; release request/reply frees such buffers.

## Control Flow

Toolbox operations are posted as single request/reply management frames. The `Tool` field selects the operation, and operation-specific fields or SGEs describe the payload. Diagnostic buffers use a two-step lifecycle: post a DMA buffer with type and size, then release it when no longer needed. ISTWI operations transfer through an SGE after selecting bus/device/address bytes. FC management encodes the selected action and corresponding union member.

## State and Persistence Behavior

Clean operations can erase persistent adapter regions and are high-impact. Diagnostic buffer posts create firmware-visible runtime buffers until released. Beacon requests alter visible hardware state until toggled back or reset. ISTWI requests may read or write external EEPROM, enclosure, or board-management state depending on bus/device address. FC management can change discovery behavior or max frame size at runtime.

## Dependencies and Integration Points

The header depends on MPI base types, `SGE_SIMPLE_UNION`, and common IOC status/log handling. It is included by `mptbase.h`. IOC facts capability bits in `mpi_ioc.h` advertise diagnostic buffer support. FC management complements FC port/device config pages and FC direct messages. Tool failures report domain-specific details through `IOCLogInfo`, including SAS diagnostic and FC log values.

## Risks and Edge Cases

Clean flags can destroy persistent firmware/configuration data. ISTWI writes can alter board devices outside normal storage paths. Diagnostic buffer addresses are 64-bit physical addresses and must remain DMA-valid until release. `MPI_DIAG_BUF_TYPE_COUNT` is a count, not a valid buffer type. FC management action info is a union; callers must initialize the member matching `Action` and clear stale bytes if firmware validates reserved fields. Beacon state should be restored on failures to avoid misleading service indicators.

## Test Signals

Safe tests include common reply decoding, diagnostic buffer post/release for each supported type, diagnostic upload format parsing, ISTWI read on known-safe devices, FC discovery actions on FC adapters, beacon on/off, and rejection of unsupported tools. Destructive clean flags should only be tested in simulation or disposable hardware. DMA tests should verify buffer lifetime and transfer length reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/message/fusion/lsi/mpi_tool.h -->
