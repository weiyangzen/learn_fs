# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 29532-31985

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 register field-layout header. It contains C preprocessor constants for bit shifts and bit masks, using the pattern `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The constants are consumed by AMDGPU register-access helpers to read, compose, and update fields in NBIO, BIF/RCC, GDC, PCIe endpoint/downstream-port, MSI-X, doorbell, HDP flush, virtualization, and root-complex PCI configuration registers.

The chunk begins in the middle of `RCC_STRAP0_RCC_BIF_STRAP2`, covers many complete NBIO address blocks, and ends in the beginning of `BIF_CFG_DEV0_RC0_PCIE_CAP`. It is not executable code; its value is the exact register-field ABI it exposes to the driver for this ASIC generation.

## Important APIs, Types, and Register Families

There are no functions, structs, enums, or persistent data objects in this chunk. The public API is the macro namespace itself. Important families include:

- `RCC_STRAP0_RCC_BIF_STRAP*`: root-complex/BIF strap fields for ASPM/LTR timers, link-down behavior, indirect access disable bits, power-brake deglitching, emergency power reduction, PCIe Gen5 gating, and vlink low-power timing.
- `RCC_STRAP0_RCC_DEV0_PORT_STRAP*`: device 0 downstream/root-port capability straps. These define advertised PCIe features such as ARI, ACS, AER, ECRC, extended tags, virtual channel count, Gen2/3/4 capability flags, L0s/L1 latencies, LTR/OBFF, equalization presets, max payload/read request sizes, hotplug and slot fields, DPC support, lane margining, alternate protocol metadata, and reset-time reporting.
- `RCC_STRAP0_RCC_DEV0_EPF0_STRAP*` and `RCC_STRAP0_RCC_DEV0_EPF1_STRAP*`: endpoint-function straps for device ID/subsystem IDs, BAR sizing and BAR type, MSI/MSI-X, power-management capability, atomic operation support, SR-IOV-related function exposure, completion timeout support, FLR, PASID/ATS/PRI-style behavior, DPA/L1 PM substates, and other endpoint capability advertisement.
- `RCC_EP_DEV0_0_*`, `RCC_DWN_DEV0_0_*`, and `RCC_DWNP_DEV0_0_*`: endpoint and downstream-port PCIe control/status fields for scratch registers, configuration decoding to hidden generation-specific registers, interrupt control/status, TX/RX controls, LTR messaging, DPA power allocation, error reporting, link-speed straps, link-bandwidth notifications, and received LTR message information.
- `RCC_DEV0_EPF0_0_*` and `RCC_DEV0_0_*`: RCC device-level fields for invalid SR-IOV access logging, doorbell aperture enablement, config aperture sizing, function identifiers, BACO request disables, VDM support, lane margining parameters, GPUIOV region controls, console IOV mode, peer register windows, bus-number/devfunc tracking, peer framebuffer offsets, XDMA aperture bounds, link-down entry/exit, common link power behavior, requester-ID restore, LTR local-switch latency, and multi-host arbitration.
- `BIF_BX0_*`: BIF/BX control fields for MM indirect access, bus coherency and flush behavior, scratch registers, VF reset behavior, MM-to-config access, link training, interrupt handling, CLKREQ and other pad controls, feature control, doorbell control/interrupts, framebuffer read/write enablement, transaction-pending status, BACO timers, memory type, GFX address LUT entries, HDP remap flush controls, BIF ring-buffer pointers, mailbox index, GPUIOV config sizing, and pad controls for PERST/PX/REFPADKIN/CLKREQ/PWRBRK.
- `BIF_BX_PF0_*`: physical-function fields for bus-master status, atomic error logs, doorbell self-ring GPA aperture base/control, HDP coherency flush controls, GPU HDP flush/invalidate/flush-only request and done bitmaps for CP0-CP9, SDMA0-1, and reserved engines, transaction-pending status, GFX address LUT bypass, mailbox transmit/receive buffers and handshakes, mailbox interrupt enablement, and VM/HV compact mailbox status/data bits.
- `RCC_DEV0_EPF0_0_GFXMSIX_*`: four MSI-X vector-table entries plus pending-bit-array fields, including message address low/high, message data, per-vector mask bits, and pending bits.
- `GDC0_*`: NGDC/GDC fields for SDP port controls, medium-grain clock gating, SOCCLK credit reservations, doorbell status, doorbell ranges for SDMA, IH, VCN, RLC, and CSDMA, ATDMA arbitration, doorbell fence enables, S2A miscellaneous controls, and NGDC power-gating/master controls.
- `BIF_CFG_DEV0_RC0_*`: root-complex PCI configuration-space fields beginning with vendor/device IDs, command/status, revision/class/header/BIST, BARs, bus numbering, IO/memory/prefetchable windows, bridge control, PM capability list/capability/status-control, and the first fields of the PCIe capability header.

## Control Flow and Data Flow

This header contributes no runtime control flow by itself. Runtime flow is created when AMDGPU code includes this file together with the matching NBIO 7.7.0 offset header and passes register names through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

Typical data flow is:

1. Driver code selects an NBIO 7.7.0 register offset from `nbio_7_7_0_offset.h`.
2. The register value is read from the SOC15, PCIe-port, MMIO, or config-space access path.
3. A field macro from this chunk supplies the exact mask and shift for extraction or update.
4. The updated value is written back only where the hardware register permits writes.

The repeated request/done bitmaps for HDP flush and invalidate operations establish an important synchronization pattern: software or a GPU engine asserts a request bit for an engine such as CP or SDMA, and later observes the matching done bit before assuming HDP-visible memory or register state is coherent.

## State and Persistence Behavior

The macros are compile-time constants and persist only in the compiled driver image. The hardware fields they describe have mixed persistence:

- Strap fields represent hardware/firmware strap-derived capability and policy state. They generally influence enumeration, advertised PCIe capabilities, link-power behavior, and feature enablement.
- Control fields such as doorbell aperture enable, MM indirect access controls, XDMA bounds, peer offsets, bus/devfunc lists, BACO controls, clock-gating, and power-gating controls are mutable runtime hardware state.
- Status/log fields such as SR-IOV invalid access, doorbell interrupts, transaction-pending bits, atomic error logs, MSI-X pending bits, and HDP flush done bits are transient hardware state and may have write-clear or handshake semantics defined outside this header.
- PCI configuration-space fields mirror PCI/PCIe configuration registers exposed to the host, including command/status, bridge windows, power-management capability, and PCIe capability metadata.

The header does not encode reset values, access permissions, write-one-to-clear behavior, required polling timeouts, ordering barriers, or ownership rules. Those semantics must come from the generated default headers, AMD hardware documentation, and the AMDGPU call sites using these macros.

## Dependencies and Integration Points

The direct companion is `nbio_7_7_0_offset.h`, which supplies register offsets for the same register names. AMDGPU's NBIO v7.7 implementation includes both headers and uses the masks with SOC15 and PCIe access helpers to initialize NBIO state, set doorbell and HDP flush behavior, configure interrupt and clock/power features, and query PCIe or revision data.

This chunk also depends conceptually on:

- Linux PCI/PCIe configuration-space semantics for command/status, bridge windows, power management, MSI/MSI-X, AER, ACS, ARI, DPC, LTR, OBFF, equalization, and lane margining fields.
- AMDGPU doorbell, IH, SDMA, CP, RLC, VCN, HDP, SR-IOV/GPUIOV, BACO, ATDMA, and GDC subsystems that program the registers represented here.
- Hardware-generated register databases. The names and bit positions are ASIC-generation-specific and should remain synchronized with offset/default headers for NBIO 7.7.0.

## Risks and Edge Cases

- A wrong mask or shift silently corrupts adjacent fields during read-modify-write operations. This is especially risky for packed fields such as PCI command/status, bridge windows, PM status-control, strap capability words, and doorbell range registers.
- The chunk includes security- and isolation-relevant fields: SR-IOV invalid access logging, IOV enable/function identifiers, GPUIOV region controls, peer framebuffer offsets, doorbell apertures, MM indirect access disables, and mailbox handshakes. Incorrect use can expose registers or memory across PF/VF or host/guest boundaries.
- Link and power-management fields affect PCIe link training, low-power entry/exit, LTR/ASPM behavior, BACO, clock gating, and power gating. Incorrect programming can produce hangs, missed PME behavior, poor power use, or link instability.
- Doorbell and HDP flush/invalidate bitmaps are synchronization-sensitive. Missing a request/done bit, using the wrong engine bit, or failing to poll/clear correctly can leave GPU memory or register state incoherent.
- PCIe capability strap fields alter what the device advertises to the host. Inconsistent capability bits can cause the OS PCI core to enable features the hardware path cannot actually support.
- Register names are highly repetitive across functions, ports, and generations. Copying a same-looking macro from another NBIO generation or from EPF0 to EPF1/port/root-complex space can target the wrong field.
- Several fields are reserved or partially reserved. Software should preserve reserved bits unless a call site has explicit hardware guidance.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-observation based:

- Build coverage for AMDGPU configurations that include `nbio_7_7_0_sh_mask.h` with `nbio_7_7_0_offset.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`.
- Compile-time failures from missing or renamed macros in NBIO v7.7 call sites.
- PCI enumeration and `lspci -vv` output matching expected vendor/device/class IDs, bridge windows, PM capability, PCIe capability, MSI/MSI-X state, AER/ACS/ARI/DPC/LTR/OBFF exposure, max payload/read-request limits, and link capability fields.
- Doorbell smoke tests for CP, SDMA, IH, VCN, RLC, and CSDMA ranges, including doorbell fence behavior where enabled.
- HDP flush/invalidate tests that assert request bits and observe matching done bits for CP and SDMA engines.
- SR-IOV/GPUIOV tests that exercise VF enable/disable, invalid access logging, function identifiers, peer offsets, console IOV mode, and VM/HV mailbox handshakes.
- Power-management tests covering ASPM/LTR, BACO entry/exit, clock-gating/power-gating controls, D-state transitions, PME behavior, and link-down recovery.
- Error-path tests for PCIe AER/error-reporting fields, atomic error logging, completion timeouts, MSI-X masking/pending bits, and BIF transaction-pending status during reset or teardown.
