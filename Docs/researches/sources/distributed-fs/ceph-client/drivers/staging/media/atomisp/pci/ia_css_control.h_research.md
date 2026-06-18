<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h` is CSS lifecycle control API for initialization, SP startup/shutdown, and status probing. It sits above the Hive/CSS device wrappers and is consumed by AtomISP host driver code and generated CSS support code.

## Important APIs, Types, and Functions

Important APIs/types are ia_css_init(), ia_css_uninit(), ia_css_enable_isys_event_queue(), SP/ISP status probes, and ia_css_start_sp()/ia_css_stop_sp(). These definitions describe CSS lifecycle, firmware, buffers, statistics, events, IRQs, frames, input ports, or generated ISP configuration data depending on the file.

## Control Flow

For pure headers, control flow is supplied by callers and implementations elsewhere: the header defines the objects passed between host code, CSS firmware loaders, stream/pipe setup, interrupt handling, and buffer/statistics queues. For generated configuration code, each `ia_css_configure_*()` function checks whether binary config offsets exist, skips zero-sized blocks, computes the DMEM offset, and calls the matching kernel-specific config copy helper.

## State and Persistence Behavior

The headers do not own memory, but many structures model persistent runtime state: firmware blob metadata, binary memory offsets, frame planes, event records, IRQ masks, input-port setup, and statistics buffers. The configuration implementation mutates `binary->mem_params.params[IA_CSS_PARAM_CLASS_CONFIG][IA_CSS_ISP_DMEM]` in host memory before that parameter block is sent to the ISP.

## Dependencies and Integration Points

Dependencies include `ia_css_types.h`, stream/pipe/binary/frame headers, Linux `BIT()` helpers, generated ISP kernel host headers, and the environment/device-access callbacks. Integration points are AtomISP stream setup, firmware loading, SP/ISP startup, HMM-backed buffers, interrupt/event delivery, and generated ISP binary parameter memory.

## Risks and Edge Cases

The dominant risk is ABI drift with firmware and generated binaries. Enum masks must stay synchronized with SP event IDs; structure sizes are often checked with static assertions; frame/statistics allocation must match grid dimensions; and generated config offsets must be bounds-correct before writing into DMEM parameter arrays. Null pointers are only partially guarded in the generated config functions.

## Test Signals

Signals include compile tests with generated headers present, static assertions for structure sizes, firmware load/start smoke tests, frame allocation/free tests across formats, IRQ/event dequeue tests, statistics translation tests for 3A/DVS grids, and config-writer tests that verify the expected DMEM bytes are updated or skipped for zero-sized blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_control.h -->
