# sources/distributed-fs/ceph-client/drivers/staging/greybus/light.c

## Purpose
Greybus Lights protocol driver. It discovers remote lights/channels, registers Linux LED class devices, flash LED devices, and optional V4L2 flash subdevices, and applies brightness, blink, color, fade, flash intensity, strobe, timeout, and fault operations through Greybus.

## Important APIs, Types, And Functions
`struct gb_lights` owns the connection, light count, light array, and lock. `struct gb_light` tracks one light, channels, flash/V4L2 state, and readiness. `struct gb_channel` stores channel descriptors, LED/flash classdevs, attributes, settings, active/releasing state, and a mutex. Key paths include `gb_lights_create_all()`, `gb_lights_light_config()`, `gb_lights_channel_config()`, `gb_lights_register_all()`, brightness/blink/flash ops, and `gb_lights_request_handler()`.

## Control Flow
Probe validates a single lights CPort, enables TX only, queries light count and each light/channel descriptor, enables RX, registers LED devices, and drops runtime PM. Channel configuration builds LED names, sysfs attribute groups for color/fade, operation callbacks, and flash constraints. Flash channels may attach torch channels and register V4L2 flash devices. Unsolicited config events release, reconfigure, and re-register the affected light under `lights_lock`.

## State And Persistence
Remote configuration is mirrored in allocated light/channel objects. Active LED state affects runtime-PM references: brightness/blink paths retain a PM reference while a channel becomes active and release it when inactive. Attribute values such as color/fade and flash settings are cached in memory.

## Dependencies And Integration Points
Uses Greybus Lights protocol, Linux LED class, LED flash class, optional V4L2 flash LED class, sysfs device attributes, runtime PM, and Greybus bundle lifecycle.

## Risks
Registration is multi-stage and error unwinds must avoid double-freeing channel names, attributes, and classdevs. Runtime-PM reference handling around active lights is subtle. Dynamic reconfiguration events race with user LED operations unless `releasing`, LED locks, and `lights_lock` are respected.

## Test Signals
Test descriptor validation, zero lights/channels, normal LED channels, multicolor/fader attrs, blink, flash/torch/indicator combinations, V4L2 enabled/disabled builds, config events, disconnect during active LED, and all partial registration failure unwinds.
