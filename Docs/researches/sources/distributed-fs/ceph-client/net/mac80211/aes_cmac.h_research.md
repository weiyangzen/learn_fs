# sources/distributed-fs/ceph-client/net/mac80211/aes_cmac.h

Purpose: this header declares the mac80211 AES-CMAC MIC calculation helper used by management frame protection code. It keeps the CMAC implementation detail out of WPA/key paths while exposing the prepared-key type from the kernel AES CBC-MAC support.

Important API and types: the header includes `<crypto/aes-cbc-macs.h>` so callers can use `struct aes_cmac_key`. It declares `ieee80211_aes_cmac()` with key, AAD, frame data, data length, MIC output, and MIC length arguments.

Control flow and contract: the declared function calculates a MIC over WLAN-specific AAD and frame body data. Callers must provide a prepared CMAC key, an AAD buffer with the frame-control information expected by the implementation, a frame body whose final `mic_len` bytes represent the MIC field, and an output buffer large enough for the requested MIC.

State and persistence behavior: the header defines no state. Persistent key state is held by mac80211 key objects in `key.c`; `aes_cmac.c` consumes that state without owning it.

Dependencies and integration: direct users are WPA management protection routines in `wpa.c` and key preparation in `key.c`. The helper is part of `mac80211.o` through the Makefile, so it is available internally without module boundary complexity.

Risks: because only one generic MIC function is exposed, misuse with the wrong `mic_len` or an incorrectly prepared AAD buffer will produce valid-looking but non-interoperable MICs. Compile-time type checking covers the key pointer type but not buffer sizing.

Test signals: compile coverage validates prototypes. Runtime coverage comes from BIP-CMAC transmit/decrypt tests, protected management frame association tests, and negative MIC/replay tests.
