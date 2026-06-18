<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.c

## Purpose
Provides shared Geode board helpers that describe GPIO keys and LEDs using software nodes and create platform devices for generic `gpio-keys-polled` and `leds-gpio` drivers.

## Important APIs, Types, And Functions
`geode_create_restart_key()` registers the cs5535 GPIO chip node, a `gpio-keys` parent, and a restart-key child with `KEY_RESTART`. `geode_create_leds()` builds per-LED software nodes with `gpios` and `linux,default-trigger` properties. `struct geode_led` is declared in the companion header.

## Control Flow
Board files call the restart-key helper first so the shared GPIO chip software node exists, then call LED creation. Allocation builds node arrays, property arrays, and GPIO references; registration creates platform devices; error paths unregister nodes and free allocated names/properties.

## State And Persistence
Software-node groups and platform devices remain registered after boot. LED node names are allocated dynamically and intentionally retained on success because the software-node/device lifetime needs them.

## Dependencies And Integration Points
Integrates Linux software nodes, GPIO lookup by fwnode, input key codes, LED class triggers, and platform-device registration. Consumers are ALIX, GEOS, and net5501 board files.

## Risks And Edge Cases
The helper supports only `MAX_LEDS` of 3; exceeding it returns `-EINVAL`. Success paths do not provide teardown because callers are built-in init code. Ordering matters for shared GPIO node registration.

## Test Signals
Successful creation of `gpio-keys-polled` and `leds-gpio` devices, absence of software-node registration errors, and functioning LED triggers/key events indicate correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geode-common.c -->
