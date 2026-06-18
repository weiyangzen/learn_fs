# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/cfg_space.c

Purpose: emulates a vGPU PCI configuration space, including writable-bit behavior, BAR sizing/programming, PCI command memory enable transitions, power state tracking, opregion hooks, and reset to defaults.

Important APIs/types/functions: public entry points are `intel_vgpu_emulate_cfg_read()`, `intel_vgpu_emulate_cfg_write()`, `intel_vgpu_init_cfg_space()`, and `intel_vgpu_reset_cfg_space()`. Internal helpers include `vgpu_pci_cfg_mem_write()`, `emulate_pci_command_write()`, `emulate_pci_rom_bar_write()`, `emulate_pci_bar_write()`, `map_aperture()`, and `trap_gttmmio()`.

Control flow: reads validate size/range and copy from virtual config memory. Writes validate size/range, then special-case PCI command, ROM BAR, regular BARs, SWSCI, and opregion base writes. Standard config writes apply byte-level RW masks and emulate RW1C status behavior. BAR writes implement all-ones sizing and normal GPA programming, toggling MMIO trapping and aperture mapping according to memory enable state.

State and persistence: stores emulated config bytes in `vgpu_cfg_space(vgpu)`, tracks BAR size and mapped/trapped state in `vgpu->cfg_space.bar[]`, records PMCSR offset, and sets `vgpu->d3_entered` on D3hot writes. Init copies firmware-provided config defaults, hides stolen memory, clears command bits and BAR high halves, sizes BAR metadata from the host PCI device, and locates PM capability.

Dependencies and risks: depends on PCI config constants, GVT firmware config snapshots, opregion emulation, and vGPU BAR helper APIs. Risks include unaligned partial BAR writes, masking mistakes in RW/RW1C bytes, stale aperture trap state across reset, and unsafe casting for small writes. Test signals include BAR all-ones sizing, memory enable/disable transitions, PM D3hot detection, opregion/SWSCI write paths, out-of-range rejection, and reset restoring default config while preserving primary/non-primary class selection.
