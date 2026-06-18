<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-ci.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-ci.c

## Purpose
`budget-ci.c` supports Technotrend/Hauppauge/Siemens SAA7146 budget DVB PCI cards with Common Interface but without analog video input, including optional MSP430-based IR remote decoding.

## Important APIs, Types, and Functions
`struct budget_ci` embeds common `struct budget`, CI work/status/IRQ state, EN50221 CA object, IR state, and tuner PLL address. `struct budget_ci_ir` tracks rc-core device state and partial RC5 command assembly. IR flow is `msp430_ir_init()`, `msp430_ir_interrupt()`, and `msp430_ir_deinit()`. CI callbacks mirror EN50221 memory/control/reset/TS/poll operations with DEBI addresses. `frontend_init()` attaches board-specific DVB frontends and tuners. `budget_ci_attach()`, `budget_ci_detach()`, and `budget_ci_irq()` integrate with SAA7146.

## Control Flow
Attach allocates state, initializes the common budget core, registers the rc-core IR device, probes/initializes CI, stores adapter private data, attaches/registers the appropriate frontend, and installs common budget hooks. IRQs queue bottom-half work for MSP430 IR on MASK06, delegate TS IRQs on MASK10, and queue CI work on MASK03 when supported. CI init enables DEBI pins, validates CI firmware/version, chooses polling versus IRQ flags, registers EN50221, configures GPIO edge direction, enables interface reset, and emits a synthetic CAM change event. Frontend init switches on subsystem device IDs to attach STV0299/STV0297/TDA1004x/TDA10023/STV0288/STB0899 and matching tuner/LNB helpers.

## State and Persistence
Runtime state includes CI slot status, whether CI IRQs are usable, queued work items, rc-core device, partial RC5 command/device bytes, selected keymap/device filter, tuner PLL address, frontend pointer, and common budget DMA/DVB state. There is no persistent storage.

## Dependencies and Integration Points
The file depends on SAA7146, TTPci budget core, DVB core/frontend/tuner/LNB modules, EN50221 CA core, rc-core, I2C, workqueues, and board-specific headers such as BSBE/BSRU configs.

## Risks and Edge Cases
MSP430 IR bytes can arrive out of order or be lost; the decoder only emits when a command byte is followed by a device byte. CI firmware version `0xa2` lacks interrupts and falls back to polling. Several frontend attach paths must tear down partially attached tuner/LNB chains on failure. `msp430_ir_deinit()` unregisters and frees the rc device, which depends on rc-core ownership semantics staying compatible.

## Test Signals
Check IR keymaps and RC5 filtering for all supported subsystem IDs, CAM insert/remove/reset/ready and FR/DA IRQs, polling-only CI firmware, TS routing through CAM, frontend registration for all listed cards, S2-3200 reset timing, LNB/tuner attach failure cleanup, MASK06/MASK03/MASK10 IRQ dispatch, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ttpci/budget-ci.c -->
