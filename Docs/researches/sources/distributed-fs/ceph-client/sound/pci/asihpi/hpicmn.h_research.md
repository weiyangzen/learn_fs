# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.h

## Purpose

`hpicmn.h` declares shared adapter and control-cache interfaces used by HPI backend implementations.

## Important APIs, types, and functions

The header forward-declares `struct hpi_adapter_obj`, defines `adapter_int_func`, IRQ result constants (`HPI_IRQ_NONE`, `HPI_IRQ_MESSAGE`, `HPI_IRQ_MIXER`), and declares `struct hpi_adapter_obj` with PCI information, adapter type/index, DSP lock, crash/cache flags, private backend pointer, interrupt callback, and host-buffer status pointers.

It also declares `struct hpi_control_cache`, which stores initialization state, adapter index, control count, raw cache byte size, lookup pointer array, and pointer to the DSP cache memory. Function declarations cover adapter lookup/add/delete, control-cache lookup for whole cache or single entries, allocation/free, set-state cache synchronization, response validation, and `HPI_COMMON`.

## Control flow

There is no executable flow. The declarations define how backend files register adapters, serialize DSP access through the embedded lock, expose optional IRQ and host-buffer status integration, and share control-cache services.

## State and persistence behavior

The struct fields declared here become persistent per-adapter state once copied into the global registry in `hpicmn.c`. `priv` points to backend-specific hardware state allocated by `hpi6000.c` or `hpi6205.c`; `has_control_cache` controls whether backends try cached reads; `dsp_crashed` gates later traffic; host-buffer status pointers persist while DMA buffers are valid.

## Dependencies and integration points

The header depends on `hpi_internal.h` types through includers. It is the contract between backend implementations, common adapter registry/cache code, and upper HPI layers that need interrupt or background-buffer status information.

## Risks and test signals

Risks include lifetime mistakes around `priv` and host-buffer status pointers, backend-private allocation mismatches, stale IRQ callback pointers after delete, and shallow-copy semantics in adapter registration. Test signals are adapter create/delete, lock initialization, crash-threshold handling, IRQ query integration, host-buffer get-info calls after allocate/free, and successful cache allocation and lookup through the common API.
