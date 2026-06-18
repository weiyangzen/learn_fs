# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dvb.h

- Purpose: Declares Mantis DVB power/reset and adapter lifecycle APIs.
- Important APIs/types/functions: `enum mantis_power`, `mantis_frontend_power`, `mantis_frontend_soft_reset`, `mantis_dvb_init`, and `mantis_dvb_exit`.
- Control flow: Board files use power/reset helpers before `dvb_attach`; probe/remove use init/exit around DMA and input/UART setup.
- State and persistence: No state; functions mutate `struct mantis_pci` GPIO and DVB fields.
- Dependencies and integration points: Integrates with board-specific frontend modules and `mantis_ioc` GPIO helpers.
- Risks: Incorrect enum usage or lifecycle order can leave frontend power enabled or DVB objects partially registered.
- Test signals: Compile coverage and board attach tests for all Mantis DVB-S/S2/C/T variants.
