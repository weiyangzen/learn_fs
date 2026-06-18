# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_d.h lines 2976-3577

## Scope And Purpose

This chunk is the tail of AMDGPU's generated BIF 5.1 register address header. It contains only C preprocessor `#define` constants; there are no functions, structs, enums, local variables, or executable statements. The constants map symbolic register names to numeric register addresses for the Bus Interface (BIF), PCIe controller/link-management logic, PCIe PHY, and PIF blocks for the `PSX80` and `PSX81` instances.

The practical purpose is to give low-level AMDGPU code stable compile-time names for indirect PCIe/BIF/PHY/PIF registers. Driver code can then pass these addresses to register-access helpers, usually together with field masks from the paired `bif_5_1_sh_mask.h` header. Correctness depends on the exact numeric values: a one-bit or one-instance error in this file can redirect a read or write to the wrong hardware register without creating an obvious compile-time failure.

This range starts by completing the `PSX80_BIF_LM_*` link-management address family, then defines the full `PSX81_BIF_PCIE_*`, `PSX81_BIF_SWRST_*`, `PSX81_BIF_LM_*`, `PSX80_PHY0_*`, `PSX81_PHY0_*`, `PSX80_PIF0_*`, and `PSX81_PIF0_*` address families. It ends with the header guard close for `BIF_5_1_D_H`.

## Important APIs, Types, And Macros

There are no C APIs or types in this chunk. The exported interface is the macro namespace:

- `ixPSX80_BIF_LM_*` and `ixPSX81_BIF_LM_*` name PCIe link-management registers such as TX/RX lane mux controls, lane enable, PRBS control, and power-control registers.
- `ixPSX81_BIF_PCIE_*` names PCIe controller registers for scratch/debug state, RX NAK counters, controller/config/bus controls, link-controller state/status, last received/transmitted TLP capture, I2C register access, port status, performance counters, strap registers, PRBS status/counters, and the controller-side soft-reset command/control region.
- `ixPSX81_BIF_SWRST_*` names command/status, general-control, command, and control registers used for BIF/PCIe soft-reset sequencing.
- `ixPSX80_PHY0_COM_COMMON_*` and `ixPSX81_PHY0_COM_COMMON_*` name common PCIe PHY registers for fuses, electrical idle, design-for-test/debug, de-emphasis selection, lane power management, adaptation controls, lane control, TX/RX test debug, and CDR phase/frequency controls.
- `ixPSX80_PHY0_RX_*` and `ixPSX81_PHY0_RX_*` name RX command-bus, RX control, DLL control, RX test, electrical-idle debug, adaptation, FOM calculation, adaptation-bypass, debug-bypass, and adaptation-debug registers. Each group has a broadcast address and per-lane addresses for lanes 0 through 7.
- `ixPSX80_PHY0_TX_*` and `ixPSX81_PHY0_TX_*` name TX command-bus, DFX, de-emphasis, margin/de-emphasis test/status, TX control, and TX global command-bus registers, again with broadcast and lane 0 through 7 variants.
- `ixPSX80_PHY0_HTPLL_ROPLL_*`, `ixPSX81_PHY0_HTPLL_ROPLL_*`, `ixPSX80_PHY0_LCPLL_LCPLL_*`, and `ixPSX81_PHY0_LCPLL_LCPLL_*` name ring/HT PLL and LC PLL power, control, test/debug, frequency-mode, update, fuse/process, and VCO-control registers.
- `ixPSX80_PIF0_*` and `ixPSX81_PIF0_*` name PIF scratch/debug/strap/control, TX/RX control, global override, command-bus status/control, and per-lane override registers for lanes 0 through 7.

The naming convention matters. `ix` prefixes indicate indexed or indirect register addresses rather than the ordinary `mm` register offsets at the start of the file. The `PSX80` and `PSX81` prefixes distinguish two sibling PCIe/PHY/PIF address spaces: for example the `PSX80` BIF PCIe region is based around `0x1400000`, while `PSX81` is based around `0x1410000`; `PSX80_PHY0` uses `0x120...` addresses, while `PSX81_PHY0` uses `0x121...`; `PSX80_PIF0` uses `0x110...`, while `PSX81_PIF0` uses `0x111...`.

## Control Flow

This chunk has no runtime control flow. It shapes caller behavior by providing the register addresses that consumers use in hardware read, write, and read-modify-write sequences.

A typical consumer flow is:

1. Select the correct BIF 5.1 register header for the ASIC/IP generation.
2. Choose an `ixPSX80_*` or `ixPSX81_*` macro for the intended PCIe, BIF, PHY, PLL, or PIF register.
3. Access the register through the AMDGPU register I/O layer or through a PCIe/indirect register-access path.
4. If modifying fields, combine this address macro with field masks and shifts from `bif_5_1_sh_mask.h`.
5. Poll status, program controls, clear counters, or trigger state changes according to the hardware block's access semantics.

The line range is mainly an address map, so branching and sequencing live in callers such as VI-era interrupt handling, UVD setup, PCIe management, power-management, diagnostics, and hardware bring-up code. Files such as `tonga_ih.c`, `cz_ih.c`, `iceland_ih.c`, and `uvd_v6_0.c` include `bif_5_1_d.h`; the IH files also include `bif_5_1_sh_mask.h` and use the register/mask pattern through `RREG32()`, `WREG32()`, and `REG_SET_FIELD()` for BIF interrupt-control registers. This chunk's `ix*` addresses support the same generated-register contract for indirect PCIe/PHY/PIF blocks rather than ordinary `mm*` offsets.

## State And Persistence Behavior

The header chunk stores no Linux or driver state. It defines names for hardware registers whose values live in the GPU and PCIe/PHY/PIF blocks.

Registers named here can expose or control persistent hardware state such as link-management muxing, lane enablement, PRBS mode and error counters, PCIe controller counters and captured TLP data, soft-reset command state, PHY fuses, electrical-idle detection, RX/TX adaptation and debug controls, PLL power/control state, and per-lane PIF override configuration. Those hardware values may persist until a later driver write, firmware/SMU action, link retrain, soft reset, suspend/resume transition, BACO or power-gating transition, hot reset, or full device reset.

The header does not encode register access semantics. Some addresses likely identify read-only status, some are writable controls, some may be sticky status or counter registers, and some control fields may be self-clearing or safe only in specific link states. Callers must rely on hardware documentation, generated field masks, and established driver sequencing to avoid treating a diagnostic/status address like an ordinary writable configuration register.

## Dependencies And Integration Points

The direct dependency is only the C preprocessor and the `BIF_5_1_D_H` include guard. In practice, this file is part of a generated AMD ASIC register-header set:

- `bif_5_1_d.h` supplies register addresses.
- `bif_5_1_sh_mask.h` supplies the bit masks and shifts for fields inside those registers.
- AMDGPU register helpers such as `RREG32()`, `WREG32()`, `REG_SET_FIELD()`, and PCIe/indirect variants perform the actual I/O.
- The surrounding VI/Polaris-era AMDGPU driver chooses this BIF generation through include selection in IP blocks such as interrupt handling and UVD support.

Important integration points for this chunk are PCIe link-management and diagnostics paths. `BIF_LM_*` addresses support lane muxing, lane enable, PRBS, and power-control operations. `BIF_PCIE_*` addresses support controller status, link-controller state capture, performance counters, straps, PRBS counters, last-TLP debug capture, and soft-reset controls. `PHY0_*` addresses support common PHY configuration, RX/TX lane programming, RX adaptation/FOM/debug, TX margin/de-emphasis/control, and PLL control. `PIF0_*` addresses support lane overrides and command-bus/global PIF controls.

The source path is under a repository named `ceph-client`, but this file is AMDGPU Linux kernel driver register metadata. There is no Ceph filesystem behavior in this chunk.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These macros are raw numeric addresses; if a macro points at the wrong base, lane, or instance, the compiler will still accept callers, but runtime reads and writes will target the wrong register.

The `PSX80` and `PSX81` families are intentionally similar and differ mostly by address-space base. Copy/paste or generation mistakes that swap `0x120...` with `0x121...`, `0x110...` with `0x111...`, or `0x140...` with `0x141...` would affect only one instance and could be hard to diagnose on systems that do not exercise both paths.

The lane-indexed PHY and PIF definitions are repetitive and vulnerable to lane-offset errors. RX lane addresses step by `0x100` from lane 0 through lane 7, TX lane addresses use a separate `0x...2000`-style base and also step by `0x100`, and broadcast addresses use high `0xfe` or `0xff` lane-selector encodings. A swapped lane suffix or broadcast/per-lane mix-up could make debugging tools report the wrong lane, power down the wrong lane, or apply an adaptation override globally when a per-lane write was intended.

Several register groups control low-level link stability. Misuse of link-management power-control, PRBS, PIF lane override, RX adaptation, TX de-emphasis, PLL power/control, or BIF soft-reset addresses can cause link retraining failures, reduced link width/speed, transient GPU disappearance, or persistent PCIe errors until reset.

This chunk begins after the first two `ixPSX80_BIF_LM_PCIETXMUX*` entries, which are in the previous chunk. The final per-file reconciliation should keep the complete `PSX80_BIF_LM_*` family together across the chunk boundary.

## Test Signals

Useful validation is mostly build-time and hardware-observable:

- Kernel build coverage for AMDGPU configurations that include `bif_5_1_d.h` catches missing or renamed macros.
- Register smoke tests or driver bring-up on BIF 5.1 ASICs should read sensible values from `PSX80` and `PSX81` PCIe, PHY, and PIF address spaces.
- PCIe link speed and width should remain stable across boot, reset, suspend/resume, runtime power transitions, and link retrain operations.
- PRBS diagnostics should show counters changing on the expected lanes and clear through the expected control/status registers.
- PHY/PIF lane override and power-management testing should affect only the intended lane or broadcast domain.
- PLL programming and power transitions should not produce hangs, link drops, or repeated recovery/equalization loops.
- Interrupt/UVD/IP-block builds that include this header should continue to compile with the paired `bif_5_1_sh_mask.h` field definitions.

Regression symptoms from bad constants include wrong debug/status readings, PRBS errors attributed to the wrong lane, failed lane power transitions, unexpected link downtraining, AER or PCIe error noise, resume failures, GPU resets during link-management operations, or inability to access the intended indirect register instance.

## Cross-Chunk Notes

The previous chunk of `bif_5_1_d.h` contains the ordinary `mm*` BIF offsets, much of the base BIF/PCIe address map, and the start of the `PSX80_BIF_PCIE` and `PSX80_BIF_LM` families. This chunk completes the file by adding the second `PSX81` PCIe/BIF instance plus the repeated PHY/PIF address families for `PSX80` and `PSX81`. The final per-file document should treat both chunks as one generated hardware address map paired with `bif_5_1_sh_mask.h`, not as executable driver logic.
