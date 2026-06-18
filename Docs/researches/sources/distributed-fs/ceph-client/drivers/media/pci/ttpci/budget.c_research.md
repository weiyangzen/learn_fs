
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget.c

## Purpose
This is the board-specific driver for SAA7146 budget DVB PCI cards without analog input or CI. It binds PCI subsystem IDs to `budget_info`, attaches demodulator/tuner/LNB helper drivers over the I2C adapter created by `budget-core.c`, implements GPIO-driven DiSEqC/tone/voltage helpers for selected boards, and registers the SAA7146 extension.

## Important APIs, Types, And Functions
The attach/detach entry points are `budget_attach` and `budget_detach`, wired into `struct saa7146_extension budget_extension`. Frontend setup is centralized in `frontend_init`, which switches on `pci->subsystem_device`. Tuner programming helpers include `alps_bsrv2_tuner_set_params`, `alps_tdbe2_tuner_set_params`, `grundig_29504_401_tuner_set_params`, `grundig_29504_451_tuner_set_params`, and `s5h1420_tuner_set_params`. Satellite control helpers include `Set22K`, `SendDiSEqCMsg`, `budget_set_tone`, `budget_diseqc_send_master_cmd`, `budget_diseqc_send_burst`, and `SetVoltage_Activy`. The file defines many frontend config structures for VES, STV, L64781, TDA, S5H, LNBP/ISL/LNBH companion chips.

## Control Flow
Module load registers the SAA7146 extension. On PCI match, `budget_attach` allocates `struct budget`, stores it in `dev->ext_priv`, calls `ttpci_budget_init`, then calls `frontend_init`. `frontend_init` tries the appropriate demod/tuner chain for the subsystem ID, often probing alternate demods in order, mutating frontend ops for tuner `set_params`, tone, DiSEqC, voltage, and firmware callbacks. If a chain succeeds, it registers the frontend on the DVB adapter; otherwise it logs the vendor/device/subsystem tuple. Detach unregisters and detaches the frontend, calls `ttpci_budget_deinit`, frees the budget object, and clears `ext_priv`.

## State And Persistence
The persistent board identity is the PCI subsystem ID table; runtime state lives in `struct budget` and in frontend private data such as `tuner_priv`. Module parameters are `diseqc_method` and `adapter_nr`. GPIO lines are used as hardware state for tone, DiSEqC, voltage, and reset sequencing, but nothing is persisted outside hardware registers.

## Dependencies And Integration Points
This file is a hub for many DVB frontend modules: `stv0299`, `ves1x93`, `ves1820`, `l64781`, `tda8083`, `s5h1420`, `tda10086`, `tda826x`, `lnbp21`, `stv6110x`, `stv090x`, `isl6423`, and `lnbh24`. It depends on the common exported APIs from `budget-core.c`, SAA7146 PCI extension registration, Linux I2C transfers, firmware loading for TDHD1, and DVB frontend registration.

## Risks
The switch table encodes many historical boards and fallback probes; incorrect ordering can attach the wrong frontend. GPIO timing for DiSEqC and reset uses busy waits and sleeps and is hardware-revision sensitive. Some configs, notably `tt1600_stv090x_config`, are mutated after tuner attach, so shared static config state can be surprising across devices. Error paths detach partially constructed frontends, but companion attach failures must be checked carefully to avoid dangling frontend ops.

## Test Signals
Test by loading the module on each supported subsystem ID and checking frontend registration, tuner lock, DiSEqC/tone/voltage behavior, and MPEG-TS streaming through the core demux. Logs should show expected tuner-detection messages and no "Frontend registration failed" or missing LNB/tuner errors. For TT S2/Omicom paths, validate STV090x/STV6110x plus LNB controller attachment and repeated tune cycles.
