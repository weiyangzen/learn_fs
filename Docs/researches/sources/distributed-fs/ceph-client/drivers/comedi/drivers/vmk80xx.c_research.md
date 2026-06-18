# sources/distributed-fs/ceph-client/drivers/comedi/drivers/vmk80xx.c

## Purpose
This COMEDI USB low-level driver supports Velleman K8055/VM110 and K8061/VM140 boards. It exposes instruction-based analog input/output, digital input/output, counters, and K8061 PWM using synchronous USB interrupt or bulk packet exchanges.

## Important APIs, Types, And Functions
`struct vmk80xx_board` describes per-model capabilities such as channel counts, ranges, maxdata, and PWM availability. `struct vmk80xx_private` stores endpoint descriptors, a semaphore limiting concurrent USB packet access, RX/TX buffers, and model type. USB transport is abstracted by `vmk80xx_read_packet()`, `vmk80xx_write_packet()`, and `vmk80xx_do_bulk_msg()`, with K8055 using interrupt endpoints and K8061 using paired bulk transfers.

COMEDI callbacks include `vmk80xx_ai_insn_read()`, `vmk80xx_ao_insn_write()`, `vmk80xx_ao_insn_read()`, `vmk80xx_di_insn_bits()`, `vmk80xx_do_insn_bits()`, `vmk80xx_cnt_insn_read()`, `vmk80xx_cnt_insn_config()`, `vmk80xx_cnt_insn_write()`, `vmk80xx_pwm_insn_read()`, and `vmk80xx_pwm_insn_write()`. Attach helpers are `vmk80xx_find_usb_endpoints()`, `vmk80xx_alloc_usb_buffers()`, `vmk80xx_reset_device()`, `vmk80xx_init_subdevices()`, `vmk80xx_auto_attach()`, and `vmk80xx_detach()`.

## Control Flow
Probe passes the USB ID's `driver_info` to COMEDI auto configuration. Attach selects board info, allocates private data, initializes a semaphore count of 8, finds suitable endpoints, allocates endpoint-sized buffers with a 64-byte minimum, stores interface data, resets K8055 output state, and registers subdevices. Each instruction operation takes `limit_sem`, prepares or reads packet bytes according to model-specific register layout, performs one USB transfer per requested sample or update, then releases the semaphore.

AI reads select K8055 AI registers or K8061 channel command bytes. AO writes update model-specific output registers and K8061 AO can be read back by sending `VMK8061_CMD_RD_AO`. Digital input decodes K8055 bit layout or reads K8061 byte directly. Digital output uses COMEDI state update logic and optionally reads K8061 DO state back. K8055 counters support debounce-time writes using an integer square-root conversion and reset commands; K8061 counters are read/reset only. K8061 PWM values are split into low two bits and upper bits according to vendor DLL behavior.

## State And Persistence
The driver keeps shared USB TX/RX buffers and COMEDI digital output state. K8055 output state is initialized by reset/write during attach because outputs cannot be read back. AO and PWM state mostly resides on hardware; only K8061 readback commands query it. No async streaming state exists.

## Dependencies And Integration Points
The driver depends on COMEDI USB auto configuration, Linux USB endpoint discovery and synchronous message APIs, COMEDI range helpers, and board USB IDs under vendor `0x10cf`. It registers a `vmk80xx` COMEDI driver paired with a USB driver and supports multiple product IDs for both K8055 and K8061 families.

## Risks And Edge Cases
`vmk80xx_do_bulk_msg()` ignores return values from its write and read bulk messages, so K8061 transport failures can be masked. The semaphore count of 8 allows several threads into shared buffers at once, which does not provide exclusive packet-buffer protection; if concurrent instructions occur, TX/RX buffer contents can race. K8061 counter indexing is opaque and marked questionable in comments. Counter debounce conversion clamps to 7450 ms but notes overflow prevention is incomplete. K8055 output reset is best-effort because its return value is ignored by attach.

## Test Signals
Useful signals include successful endpoint discovery for interrupt versus bulk models, attach reset on K8055, correct DIO bit remapping for K8055, K8061 AO/PWM readback consistency, counter reset/write behavior, and tests that run concurrent instructions to expose shared buffer races.
