# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineFactory.hh

## Purpose
Provides header-only helpers for mapping a configured engine name to a `BalancerEngineT` enum and constructing the corresponding concrete balancer engine.

## Important APIs, types, and functions
`get_engine_type(std::string_view name)` maps `"minmax"` to `BalancerEngineT::minmax`, `"freespace"` to `BalancerEngineT::freespace`, and defaults every other name to `BalancerEngineT::stddev`. `make_balancer_engine(BalancerEngineT engine_t)` returns a raw `new` `MinMaxBalancerEngine`, `FreeSpaceBalancerEngine`, or default `StdDevBalancerEngine`.

## Control flow
Configuration code can parse a name into an enum, then construct an engine. Unknown names silently select stddev, making stddev the compatibility/default policy. Construction is unconditional and transfers ownership of a raw pointer to the caller.

## State and persistence
No state is stored in the factory. Persistence is external, usually the configuration string that eventually reaches `get_engine_type()`.

## Dependencies and integration points
Includes `StdDevBalancerEngine.hh`, `MinMaxBalancerEngine.hh`, and `FreeSpaceBalancerEngine.hh`, so including this header pulls all concrete engine definitions. It is the factory boundary between operator/configured engine names and concrete balancing policies.

## Risks and test signals
The functions are non-`inline` definitions in a header, which can create ODR/linker issues if the header is included in multiple translation units without compiler/linker allowances. Raw pointer ownership is another risk; callers must delete or wrap the result. Silent fallback for typos can mask misconfiguration. Tests should cover name mapping, unknown-name default behavior, each enum construction, ownership cleanup through a base pointer, and multi-translation-unit builds that include the factory.
