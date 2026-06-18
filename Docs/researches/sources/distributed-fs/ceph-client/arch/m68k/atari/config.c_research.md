# sources/distributed-fs/ceph-client/arch/m68k/atari/config.c

Purpose: central Atari machine configuration, hardware probing, machine hook registration, reset, heartbeat, hardware reporting, and platform-device registration.

Important APIs are `atari_parse_bootinfo()`, `config_atari()`, `atari_switches_setup()`, `atari_get_model()`, `atari_get_hardware_list()`, and `atari_platform_init()`. It exports machine cookies, hardware presence, user switch flags, floppy-select guard, and RTC year offset.

Control flow parses bootinfo model cookies and early `switches=` options, installs machdep hooks for scheduler, IRQs, model/hardware list, reset, beep, and heartbeat, then probes hardware registers with `hwreg_present()`/`hwreg_write()`. It sets presence bits for shifters, MFPs, SCSI/DMA, PSG, PCM/CODEC, DSP, SCC/ESCC, SCU/VME, joystick, blitter, IDE, MICROWIRE, clocks, FDC speed, and ACSI fallback. It disables early transparent translation on 040/060 where safe and initializes ST-RAM allocation.

Reset flow handles Medusa/Afterburner quirks, optional ACIA reset for overscan switches, disables IRQs, resets VBR, adjusts 040/060 translation/cache/PCR state, and jumps to firmware reset address. Platform init conditionally registers EtherNAT, EtherNEC/NetUSBee, Atari SCSI, and Falcon IDE platform devices.

State includes hardware presence bitmap, switch flags, TOS-derived RTC year offset, platform resource/device structures, and hardware register side effects. Dependencies include Atari hardware headers, `stram.c`, `time.c`, `ataints.c`, `atasound.c`, debug code, and platform driver APIs.

Risks and test signals: probing can be unsafe on clones; model-specific reset is fragile; platform device detection uses direct `ioremap()`/`hwreg_present()`. Test on ST/STE/TT/Falcon/Medusa-like configs, `switches=` parsing, `/proc/hardware`, ST-RAM pool setup, reboot, and platform device probes.
