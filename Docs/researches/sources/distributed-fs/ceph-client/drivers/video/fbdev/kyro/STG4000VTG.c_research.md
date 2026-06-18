
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000VTG.c

Purpose: controls STG4000 VGA reset and DAC video timing generator (VTG) start/stop and timing register programming.

Important APIs: `DisableVGA()` toggles the VGA reset bit in `SoftwareReset` with a short busy delay. `StopVTG()` sets horizontal/vertical sync generator stop bits and clears enable bit 31 in `DACSyncCtrl`. `StartVTG()` sets bit 31 and clears stop bits. `SetupVTG()` translates `struct kyrofb_info` timing fields into horizontal and vertical DAC timing registers and sync polarity bits.

Control flow: called from Kyro mode set after RAMDAC/output shutdown. `SetupVTG()` calculates display start, borders, front/back porch starts, total counts, and special margins for 640x480 at 60/72 Hz, then writes `DACHorTim1-3`, `DACVerTim1-3`, and `DACSyncCtrl`.

State and persistence: mutates `SoftwareReset`, `DACSyncCtrl`, and DAC timing registers. It does not cache software state.

Dependencies and integration: relies on `struct kyrofb_info` fields populated by `kyrofb_set_par()` in `fbdev.c` and register macros from `STG4000Reg.h`.

Risks: polarity comments contain at least one duplicated/mismatched description, so behavior should be verified against real sync polarity expectations. Border math assumes valid totals and porch values. Busy delay is fixed and CPU-speed dependent. No explicit validation is done inside `SetupVTG()`.

Test signals: mode set across `kyro_modedb`, especially 640x480 special cases, all sync polarity combinations, VTG stop/start sequencing during blank mode changes, and register dumps for total/display/front/back timing fields.
