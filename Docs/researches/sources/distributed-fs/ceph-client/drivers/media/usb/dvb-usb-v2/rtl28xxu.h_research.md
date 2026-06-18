# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/rtl28xxu.h

Purpose: private header for the Realtek RTL28xxU DVB USB bridge driver. It declares the private device state, chip/tuner/slave-demod identifiers, USB command encodings, request/register helper structs, and register maps for USB, SYS/GPIO/I2C, and IR blocks.

Important APIs/types/functions: `struct rtl28xxu_dev` stores control buffer, chip/tuner state, cached demod page, demod adapter, RC flag, child devices, SDR platform device, slave-demod enum, and a union of RTL2830/RTL2832 platform data. `enum rtl28xxu_chip_id`, `enum rtl28xxu_tuner`, `struct rtl28xxu_req`, `struct rtl28xxu_reg_val`, and `struct rtl28xxu_reg_val_mask` define driver-local contracts. Command macros encode vendor-control `index` values.

Control flow: `rtl28xxu.c` uses these definitions for every USB request, register read/write, tuner switch, frontend/platform data setup, and RC register program sequence. Child demod/tuner headers included here provide platform data and attach types used by the implementation.

State and persistence: the header captures all runtime bridge state but allocates none by itself. Register macros describe hardware state that persists until reset or explicit writes: endpoint setup, USB DMA/FIFO, GPIO, demod control, system I2C master, and IR receive buffers.

Dependencies and integration: includes dvb-usbv2, platform device support, RTL demod headers, slave demod headers, and tuner headers. The `enum rtl28xxu_tuner` explicitly says it must stay synchronized with the RTL2832 demod driver.

Risks: coupling this header to many frontend/tuner headers increases rebuild and config fragility. The tuner enum synchronization comment is a real maintenance hazard: mismatched values could program wrong demod/tuner settings. Register-space command routing is encoded by numeric ranges in implementation and must stay aligned with this map.

Test signals: compile with all supported tuner/demod configs; verify enum values against RTL2832 demod expectations; run register read/write paths across USB, SYS, and IR spaces; validate child-device lifecycle fields are initialized and cleaned on detach.
