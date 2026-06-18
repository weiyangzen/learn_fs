# sources/distributed-fs/ceph-client/arch/m68k/atari/ataints.c

Purpose: Atari interrupt-controller setup and special IRQ allocation for autovectors, MFPs, SCC, VME, EtherNAT, and shared timer-D poll interrupts.

Important APIs are `atari_init_IRQ()`, `atari_register_vme_int()`, and `atari_unregister_vme_int()`. The primary `atari_irq_chip` starts/shuts/enables/disables machine IRQs by calling `m68k_irq_startup()`, `atari_turnon_irq()`, `atari_enable_irq()`, and matching shutdown calls. It also restores Falcon HBL handlers for `IRQ_AUTO_4` shutdown.

Control flow initializes user vectors for all Atari sources, configures ST-MFP and optional TT-MFP vector bases/masks, resets SCC when needed, programs SCU masks or HBL fallback handlers, initializes PSG and shared ST-DMA, and installs a Timer D fan-out handler for polled sub-IRQs. EtherNAT IRQs 139-140 get a CPLD-backed IRQ chip that maps/unmaps the CPLD register and avoids enabling USB at startup to prevent storms.

State includes `free_vme_vec_bitmap`, `stmfp_base.int_mask`, optional `enat_cpld` mapping, MFP/SCU/SCC hardware registers, and IRQ-core configuration. VME IRQ allocation persists through the bitmap until unregistered.

Dependencies include Atari hardware headers, `stdma_init()`, `atari_microwire_cmd()`, generic IRQ APIs, and vector table symbols. Integration is set through `mach_init_IRQ` in `config.c` and used by Atari storage, network, USB, SCC, and VME drivers.

Risks and test signals: shared MFP and EtherNAT control are prone to storms or lost interrupts; dynamic VME allocation has a bitmap bound mismatch risk because the loop scans 32 bits but checks `i == 16`. Test `/proc/interrupts`, VME register/unregister, Timer D polled IRQs, EtherNAT/NetUSBee behavior, and Falcon HBL suppression.
