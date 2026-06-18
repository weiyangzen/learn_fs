<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-av.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-av.c

## Purpose
`budget-av.c` supports KNC1/TerraTec/Satelco SAA7146 budget DVB PCI cards with analog video input and optional CI, combining DVB transport capture, frontend attachment, SAA7113 analog capture, and EN50221 CAM access.

## Important APIs, Types, and Functions
`struct budget_av` embeds `struct budget`, analog video state, CI work/status, EN50221 CA object, and a demod reinitialization flag. I2C helpers read/write tuner and decoder registers. CI callbacks implement attribute/control memory access, reset/shutdown, TS enable, and polling. `saa7113_init()` and `saa7113_setinput()` manage analog input. `frontend_init()` selects demod/tuner attachments from many subsystem IDs. `budget_av_attach()`, `budget_av_detach()`, `budget_av_irq()`, and the `saa7146_extension` integrate with the SAA7146 framework.

## Control Flow
Attach allocates state, initializes the common TTPci budget core, configures SAA7146 stream registers, probes SAA7113, and if present initializes SAA7146 VV, registers a V4L2 video device, and sets the analog input. It reads the MAC from EEPROM, stores private adapter data, attaches/registers the appropriate DVB frontend, initializes CI, and installs common budget hooks. IRQ handling delegates MASK10 transport events to the budget core. Detach unregisters analog video, CI, frontend, budget core, and frees state.

## State and Persistence
Runtime state includes current analog input, SAA7113 presence, CI slot state, `dvb_ca_en50221`, frontend pointer in embedded budget state, proposed MAC, and SAA7146 GPIO/video-port state. No persistent data is written; EEPROM MAC is read only.

## Dependencies and Integration Points
The driver depends on `budget-core` DEBI/TS helpers, SAA7146 and SAA7146 VV, DVB core/frontend/tuner modules, I2C, EN50221 CA core, EEPROM/MAC helpers, and board IDs supplied through PCI extension data.

## Risks and Edge Cases
CI polling uses both GPIO card-detect and speculative IO-memory reads because some CAM detect lines are unreliable; the speculative read can upset some CAMs, so it is gated by status/open state. Frontend support is a large board-ID switch with many magic tuner constants. Analog video registration is conditional, so cards without SAA7113 still load as DVB/CI. Some errors from `ciintf_init()` are not fatal to attach.

## Test Signals
Validate PCI ID matching, TS capture IRQs, MAC EEPROM read fallback, frontend registration for DVB-S/S2/C/T variants, analog V4L2 input switching between composite and S-Video, CI CAM insert/reset/ready/removal, TS routing through CAM on enable, and detach cleanup for both analog-present and analog-absent cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-av.c -->
