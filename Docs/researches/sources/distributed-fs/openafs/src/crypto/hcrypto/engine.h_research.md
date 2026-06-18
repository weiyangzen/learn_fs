# sources/distributed-fs/openafs/src/crypto/hcrypto/engine.h

This header defines the minimal ENGINE type and prototypes required by the OpenAFS hcrypto build. It forward-declares `struct hc_engine` as `ENGINE`, includes `hcrypto/rand.h`, and declares `ENGINE_finish`, `ENGINE_up_ref`, and `ENGINE_get_RAND`.

There is no runtime state in the header. Integration is with `engine.c` stubs and Heimdal-derived hcrypto source expecting an ENGINE API. The risk is API incompleteness if future hcrypto code begins using more ENGINE functions or struct internals. Test signals are compile/link coverage of all hcrypto sources using this header.
