# sources/distributed-fs/ceph-client/include/crypto/hmac.h

Purpose: HMAC inner and outer pad byte constants.

Important APIs/types/functions: `HMAC_IPAD_VALUE` (`0x36`) and `HMAC_OPAD_VALUE` (`0x5c`).

Control flow: none; HMAC implementations XOR normalized keys with these constants to derive inner and outer pads.

State and persistence: none.

Dependencies and integration points: used by HMAC implementations and tests.

Risks: constants are fundamental to HMAC; any change breaks compatibility. Header does not define full HMAC API.

Test signals: HMAC known-answer tests across hash functions and compile-time use by HMAC providers.
