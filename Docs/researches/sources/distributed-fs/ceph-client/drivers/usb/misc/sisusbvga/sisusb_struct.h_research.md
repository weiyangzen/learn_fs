# sources/distributed-fs/ceph-client/drivers/usb/misc/sisusbvga/sisusb_struct.h

Purpose: Mode-setting structure definitions shared by sisusb initialization and mode table code. These structures describe standard VGA modes, extended modes, reference timings, CRTC tables, VCLK programming, and a private context that points to all tables.

Important APIs and types: `struct SiS_St`, `SiS_StandTable`, `SiS_StResInfo_S`, `SiS_Ext`, `SiS_Ext2`, `SiS_CRT1Table`, `SiS_VCLKData`, `SiS_ModeResInfo`, and `SiS_Private`. `SiS_Private` stores I/O port bases, current mode flags, and const pointers to all table arrays.

Control flow: the implementation fills a `SiS_Private` context with register port addresses and table pointers, then mode-setting code indexes these structures by mode IDs, reference indices, and timing selectors to program the SiS315 graphics core through the USB bridge.

State and persistence: definitions only; actual mode state lives in driver/device registers. Risks include compact legacy VGA table layouts with many implicit indices, signed fields for ROM mode indexes, and no compile-time relationship enforcement between table indices and table lengths. Test signals include mode-switch coverage across table entries, structure layout compatibility with `sisusb_tables.h`, and build coverage for all referenced fields.
