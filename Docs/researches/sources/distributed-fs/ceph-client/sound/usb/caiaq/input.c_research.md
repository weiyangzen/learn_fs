# sources/distributed-fs/ceph-client/sound/usb/caiaq/input.c

## Purpose
Implements optional Linux input-device support for CAIAQ controllers: buttons, analog pots/faders, endless rotary encoders, jog wheels, Maschine pads, and product-specific event packet parsing.

## Important APIs, Types, and Functions
Public functions are `snd_usb_caiaq_input_init()`, `snd_usb_caiaq_input_dispatch()`, `snd_usb_caiaq_input_disconnect()`, and `snd_usb_caiaq_input_free()`. Important helpers are `decode_erp()`, `snd_caiaq_input_read_analog()`, `snd_caiaq_input_read_erp()`, `snd_caiaq_input_read_io()`, `snd_usb_caiaq_tks4_dispatch()`, `snd_usb_caiaq_maschine_dispatch()`, `snd_usb_caiaq_ep4_reply_dispatch()`, and input open/close callbacks.

## Control Flow
Initialization allocates an input device, fills name/phys/id, selects capabilities by USB product id, copies or generates keycodes, sets absolute axis ranges, configures automatic EP1 event messages, and for Traktor Kontrol X1/S4/Maschine allocates and configures an EP4 bulk input URB. Input open submits EP4 URB for products that need it; close kills it. EP1 replies are dispatched by `device.c` to `snd_usb_caiaq_input_dispatch()`, which routes analog, ERP, or IO messages. EP4 completion parses product-specific bulk packets, reports events, and resubmits the URB.

## State and Persistence
State persists in `snd_usb_caiaqdev`: `input_dev`, physical path, keycode array, EP4 URB, and EP4 buffer. Runtime event state is reported to the Linux input core, not stored beyond current buffers.

## Dependencies and Integration Points
Depends on Linux input core, USB input id helpers, CAIAQ command helpers, and product ids/spec in `device.h`. Built only when `CONFIG_SND_USB_CAIAQ_INPUT` is enabled.

## Risks
Many parsers assume minimum packet lengths only in some paths; EP1 analog/ERP/IO dispatch has limited length validation before per-product offset reads. In Maschine init, `input->absbit[0] |= MASCHINE_PAD(i)` appears to OR a code value rather than a bit mask, which deserves scrutiny. EP4 URB free occurs in `input_free()` after unregister; disconnect kills URB first. Input unregister sets core ownership expectations, so `input_dev` pointer handling must avoid double free.

## Test Signals
Test each supported input product, EP1 auto messages, EP4 open/close/requeue, short packet handling, keycode tables, ERP wraparound decode, S4 block ids, Maschine pad pressure reports, and config-disabled builds.
