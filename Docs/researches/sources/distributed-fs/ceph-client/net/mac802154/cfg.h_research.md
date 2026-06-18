# sources/distributed-fs/ceph-client/net/mac802154/cfg.h

## Purpose
`cfg.h` declares the mac802154 cfg802154 operations table for registration by the rest of the stack.

## Important APIs, Types, And Functions
It exposes `extern const struct cfg802154_ops mac802154_config_ops;`, implemented in `cfg.c`.

## Control Flow
The header has no control flow. It provides a single symbol declaration.

## State And Persistence
No state is stored here. The declared ops table is static constant data in `cfg.c`.

## Dependencies And Integration Points
Consumers include mac802154 registration code that attaches the ops table to the WPAN PHY/cfg802154 layer.

## Risks And Edge Cases
Header risk is limited to declaration drift if `cfg.c` changes the symbol type or name.

## Test Signals
Compilation and successful WPAN PHY registration through cfg802154 are the relevant signals.
