# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.h

## Purpose
`dst_ca.h` defines DST conditional-access protocol constants and a small private wrapper for the DST CA device. It is shared by `dst_ca.c` and `dst_common.h`.

## Important APIs, Types, And Functions
The header defines retry count `RETRIES` and EN50221-style CA tag constants such as `CA_APP_INFO_ENQUIRY`, `CA_APP_INFO`, `CA_INFO_ENQUIRY`, `CA_INFO`, `CA_PMT`, `CA_PMT_REPLY`, and MMI/menu/list/keypad tags under `0x9f88xx`. `struct dst_ca_private` groups a `struct dst_state *` and `struct dvb_device *`.

## Control Flow
No code executes here. The tag definitions drive `ca_send_message()` and `ca_get_message()` switch statements in `dst_ca.c`, and `RETRIES` bounds low-level CI communication retry loops.

## State And Persistence
The header defines a possible state wrapper but does not allocate or persist state. Runtime CA state actually lives in `struct dst_state` and `struct dvb_device`.

## Dependencies And Integration Points
It forward-references `struct dst_state` indirectly through usage and is included by `dst_common.h`, which exposes `dst_ca_attach()`. The constants align Linux DVB CA ioctl message payloads with the DST CI packet translation layer.

## Risks
Incorrect tag values would route CA messages to the wrong handler or make userspace/CAM negotiation fail. The unused `dst_ca_private` structure can mislead maintainers because the active implementation stores `dst_state` directly in `dvb_device.priv`.

## Test Signals
Compile coverage and successful CA ioctl dispatch for app info, CA info, PMT, and MMI tags validate this header. Retry behavior is indirectly tested by transient CI command failures recovering before `RETRIES`.
