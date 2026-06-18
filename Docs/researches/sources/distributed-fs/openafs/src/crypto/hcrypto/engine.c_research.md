# sources/distributed-fs/openafs/src/crypto/hcrypto/engine.c

This file provides stub ENGINE support for hcrypto. OpenAFS does not build hcrypto public-key/ENGINE functionality, so `ENGINE_finish` and `ENGINE_up_ref` return `-1`, and `ENGINE_get_RAND` returns `NULL`.

The API is exactly those three functions declared in `engine.h`. Control flow is trivial and stateless. Dependencies are `config.h`, local `engine.h`, and `stdlib.h`; `engine.h` pulls in `hcrypto/rand.h` for `RAND_METHOD`.

Integration is with upstream hcrypto code that references ENGINE APIs but where OpenAFS wants linkability without real engine support. Risks arise if a caller starts treating ENGINE as supported; failures are deterministic but may be unchecked by upstream code. Test signals are link success and functional tests confirming default RAND paths do not require an ENGINE.
