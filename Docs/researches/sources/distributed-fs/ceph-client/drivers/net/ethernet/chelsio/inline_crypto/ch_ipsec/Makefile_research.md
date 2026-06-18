# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/Makefile

## Purpose
Builds the Chelsio inline IPsec module from `chcr_ipsec.o` and supplies include paths for cxgb4 and Chelsio crypto headers.

## Important APIs, Types, And Functions
The Makefile sets `ccflags-y` to include `drivers/net/ethernet/chelsio/cxgb4` and `drivers/crypto/chelsio`, then maps `CONFIG_CHELSIO_IPSEC_INLINE` to module `ch_ipsec.o` with `ch_ipsec-objs := chcr_ipsec.o`.

## Control Flow
Kbuild compiles `chcr_ipsec.c` into the `ch_ipsec` module or built-in object depending on the tristate value. There is no runtime control flow in this file.

## State And Persistence
State is limited to build artifacts. The include path choice persists the source-level dependency on cxgb4 ULD and Chelsio crypto key-context helper headers.

## Dependencies And Integration Points
This build file integrates the IPsec source with cxgb4 symbols and crypto helper headers such as `chcr_core.h`, `chcr_algo.h`, and `chcr_crypto.h`. It is included via `inline_crypto/Makefile`.

## Risks
Include path drift can break compilation if cxgb4 or drivers/crypto/chelsio headers move. Module naming must remain aligned with Kconfig help text and ULD registration name.

## Test Signals
Building `CONFIG_CHELSIO_IPSEC_INLINE=m` should produce `ch_ipsec.ko`; built-in mode should link `chcr_ipsec.o` without unresolved cxgb4/crypto symbols.
