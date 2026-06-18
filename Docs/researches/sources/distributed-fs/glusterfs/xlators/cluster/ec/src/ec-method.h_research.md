# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-method.h

## Purpose
This header defines the public EC coding-method interface and constants used by the disperse translator for Galois-field erasure coding.

## Important APIs, Types, And Functions
It defines GF parameters `EC_GF_BITS`, `EC_GF_MOD`, `EC_GF_SIZE`, capacity constants `EC_METHOD_MAX_FRAGMENTS` and `EC_METHOD_MAX_NODES`, and word/chunk constants `EC_METHOD_WORD_SIZE` and `EC_METHOD_CHUNK_SIZE`. It declares lifecycle APIs `ec_method_init()`, `ec_method_fini()`, `ec_method_update()`, and data APIs `ec_method_encode()` and `ec_method_decode()`.

## Control Flow
The header itself has no control flow. Callers initialize an `ec_matrix_list_t`, use encode/decode during FOP execution, optionally request an update for CPU extension changes, then finalize the method on translator teardown.

## State And Persistence Behavior
The state is owned by the `ec_matrix_list_t` passed to the functions. The header does not persist data.

## Dependencies And Integration Points
It includes `ec-types.h` and `ec-galois.h`, binding the coding API to EC type definitions and GF arithmetic support. `ec.h` derives maximum EC nodes from these constants.

## Risks
Changing constants changes on-disk/data-layout assumptions and maximum legal disperse volume shapes. Consumers expect chunk sizes to align with buffer preparation in write/read paths.

## Test Signals
Compile-time users should agree on constants. Runtime encode/decode tests should validate that `EC_METHOD_CHUNK_SIZE` matches fragment-size assumptions in `ec.c` and offset adjustment helpers.
