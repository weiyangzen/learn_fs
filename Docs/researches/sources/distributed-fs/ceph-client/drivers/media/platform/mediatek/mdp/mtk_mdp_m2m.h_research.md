# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.h

## Purpose
This header exposes the legacy MDP mem2mem registration and context-state helper used by the core and watchdog paths.

## Important APIs, Types, and Functions
It declares `mtk_mdp_ctx_state_lock_set()`, `mtk_mdp_register_m2m_device()`, and `mtk_mdp_unregister_m2m_device()`.

## Control Flow
The core calls registration during probe and unregister during remove. The watchdog calls the state setter to mark active contexts as error.

## State and Persistence
The header itself holds no state; it gives access to context state mutation and video-device lifecycle.

## Dependencies and Integration Points
It depends on `struct mtk_mdp_ctx` and `struct mtk_mdp_dev` from `mtk_mdp_core.h`.

## Risks and Edge Cases
Callers must hold appropriate lifecycle references to contexts/devices because the prototypes do not encode ownership. State setting only ORs bits; it does not clear errors.

## Test Signals
Compile/link coverage and watchdog-triggered error-state tests validate the contract.
