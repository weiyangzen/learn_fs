# sources/distributed-fs/ceph-client/rust/macros/vtable.rs

## Purpose
`vtable.rs` implements `#[vtable]`, which lets Rust traits model Linux C vtables where optional methods are represented by null function pointers. It generates `HAS_*` associated constants that indicate which optional methods an implementation actually overrides.

## Important APIs, Types, And Functions
`vtable(input: Item) -> Result<TokenStream>` dispatches to `handle_trait(ItemTrait)` or `handle_impl(ItemImpl)`. Trait handling adds `USE_VTABLE_ATTR` and default `HAS_METHOD = false` constants. Impl handling adds `USE_VTABLE_ATTR` and `HAS_METHOD = true` constants for implemented methods unless the user already defined the constant.

## Control Flow
On traits, every trait method produces a cfg-preserving `HAS_*` bool constant. On impl blocks, explicitly defined constants are first collected to allow overrides, then each implemented method produces a cfg-preserving `HAS_* = true` constant. Applying the attribute to anything other than a trait or impl emits an error.

## State And Persistence
No runtime state is stored. Generated associated constants become compile-time signals consumed by vtable construction code elsewhere.

## Dependencies And Integration Points
It uses `syn`, `quote::ToTokens`, `HashSet`, and `helpers::gather_cfg_attrs`. It integrates with kernel traits that generate C vtables and with default methods that should never be called directly when optional.

## Risks And Edge Cases
Method names are uppercased mechanically, so unusual names or cfg combinations must be consistent between trait and impl. Required methods and optional methods both receive constants at the trait site because the impl site cannot distinguish them. Users can override generated constants, which is intentional but can lie if misused.

## Test Signals
Tests should cover trait annotation, impl annotation, cfg propagation, explicit `HAS_*` override, invalid target items, and integration with a C-vtable builder that chooses null pointers based on constants.
