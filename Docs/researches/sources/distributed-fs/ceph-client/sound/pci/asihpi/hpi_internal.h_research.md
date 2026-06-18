# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpi_internal.h

## Purpose

`hpi_internal.h` is the internal ABI hub for the AudioScience HPI driver. It defines OS integration hooks, bus/vendor IDs, message types, object types, function IDs, control attributes, message and response payload layouts, control-cache structures, host-buffer status structures, and internal entry-point declarations used by the asihpi backends.

## Important APIs, types, and functions

The header declares locked DMA memory operations (`hpios_locked_mem_alloc/free/get_phys_addr/get_virt_addr/valid`) and delay hooks, `hpi_handler_func`, compile-time assertion support, HPI bus/subsystem/buffer enums, adapter family macros, all low-level object/function IDs, and common structs such as `hpi_pci`, `hpi_resource`, `hpi_msg_format`, `hpi_msg_data`, `hpi_buffer`, `hpi_hostbuffer_status`, `hpi_message`, and `hpi_response`.

It also defines object-sized message/response tables, v1 payload buffer limits for network transport, adapter debug/Cobranet message formats, handle conversion declarations, the main `hpi_send_recv()` declaration, legacy compatibility declarations, and backend declarations `HPI_6000` and `HPI_6205`. Control-cache ABI types include `hpi_control_cache_info`, per-control cache structs for volume, meter, mux, tuner, AES3, tone/silence detector, sample clock, microphone, PAD strings, and `hpi_fifo_buffer`.

## Control flow

The header itself has no executable control flow, but it dictates runtime dispatch. Function IDs are constructed from object ID times `HPI_OBJ_FUNCTION_SPACING` plus an index; backends switch on `phm->type`, `phm->object`, and `phm->function`. Message and response unions determine how each backend copies payloads to firmware and interprets returned bytes. Buffer command enums define the multi-phase host-buffer allocate/grant/revoke/free workflow used by `hpi6205.c`.

## State and persistence behavior

No storage is allocated here, but the structures define persistent state in adapter objects, HPI messages, DSP responses, DMA host buffers, network packets, and DSP/host control caches. Layout stability is critical because firmware, compatibility ioctls, and possibly 32-bit compatibility paths depend on exact field order, size, and alignment.

## Dependencies and integration points

It includes public `hpi.h` and OS-specific `hpios.h`, and is included by all researched backend/common files. It integrates the Linux PCI/DMA layer, ALSA-facing HPI entry points, firmware DSP protocols, network/Cobranet packet paths, and legacy binary compatibility declarations.

## Risks and test signals

Risks include ABI-breaking structure changes, enum drift from firmware, endian/alignment assumptions, stale compatibility fields, function-count mismatches, payload buffer overflow, and duplicated compile-time-assert definitions across headers. Test signals include compile-time size assertions, successful message initialization and validation, 32-bit compat builds, firmware command/response compatibility, host-buffer status correctness, control-cache parsing across all control types, and broad hardware smoke tests for adapter, stream, mixer, GPIO, async event, and profile objects.
