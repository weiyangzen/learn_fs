# sources/distributed-fs/ceph-client/drivers/net/wireguard/cookie.h

## Purpose
`cookie.h` declares WireGuard cookie/MAC state structures, validation result enum, and public cookie helper functions used by handshake send/receive paths.

## Important APIs, Types, And Functions
`struct cookie_checker` contains the device-wide rotating secret, precomputed cookie encryption key, precomputed MAC1 key, secret birthdate, rwsem, and device pointer. `struct cookie` contains per-peer cookie state, last MAC1 sent, precomputed decryption/MAC1 keys, validity flags, birthdate, and rwsem. `enum cookie_mac_state` distinguishes invalid MAC, valid MAC without cookie, valid cookie but ratelimited, and valid cookie. Function prototypes cover checker/peer initialization, key precompute, packet validation, MAC insertion, cookie message creation, and cookie message consumption.

## Control Flow
The header defines the call contract: devices initialize a checker, peers initialize a cookie and precompute peer keys, send paths add MACs, receive paths validate packets and optionally issue cookie messages, and peers consume encrypted cookie replies.

## State And Persistence
All declared state is volatile memory. The birthdate fields interact with timer helpers to expire cookies and secrets. Locks protect concurrent handshake send/receive access to cookie material.

## Dependencies And Integration Points
The header includes WireGuard message definitions and rwsem support, forward-declares peers, and is consumed by cookie, send, receive, peer, and device code. It depends on Noise and message constants provided by included headers.

## Risks
Callers must respect lock expectations from the implementation, especially static identity locking before device key precompute and peer cookie locking during concurrent send/consume operations. Enum handling must preserve the distinction between ratelimited and fully valid cookies because receive paths use it for response policy.

## Test Signals
Compile all WireGuard users, exercise concurrent send/receive cookie updates under lock debugging, verify enum handling in receive policy, and test secret/cookie expiration using timer helper boundaries.
