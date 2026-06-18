# sources/control-plane/mayastor/io-engine/tests/reactor_interrupt.rs

Purpose: regression test ensuring `mayastor_env_stop` accepts `ReactorState::Interrupt` when interrupt mode is enabled.

Important APIs/types/functions: `MayastorEnvironment`, `MayastorCliArgs`, `Reactors`, `ReactorState::Interrupt`, and `mayastor_env_stop`.

Control flow: the test initializes a one-reactor environment with `interrupt_mode=true`, explicitly calls `Reactors::master().enter_interrupt_mode()`, asserts the master state is `Interrupt`, then calls `mayastor_env_stop(0)`.

State and persistence behavior: no persistence. State under test is the reactor shutdown state machine.

Dependencies and integration points: SPDK environment interrupt mode and io-engine shutdown handling.

Risks: it does not send a real signal; it only reproduces the reactor state transition used by normal interrupt-mode startup.

Test signals: state equals `Interrupt` and shutdown does not panic.
