# sources/control-plane/mayastor/test/python/tests/rpc/test_interrupt_mode.py

Purpose: smoke tests for io-engine reactor interrupt mode. The file is explicitly scoped to regressions where the environment flag is ignored, idle reactors busy-poll, or futures fail to wake sleeping reactors.

Important APIs and control flow: `INTERRUPT_ENABLED` reads `ENABLE_INTERRUPT_MODE`; `interrupt_only` skips all tests unless it is `true`. `test_reactor_state_is_interrupt` searches container logs for global interrupt enablement and reactor transition messages. `test_idle_cpu_is_low` waits, calls `docker stats --no-stream`, parses CPU percentage, and asserts below 50%. `test_wakeup_from_sleep` times a `mayastor_info()` gRPC round trip and asserts under 500 ms.

State, dependencies, and integration: state is process log output and runtime CPU usage of `ms1`. It depends on Docker CLI, stable log strings, monotonic timing, and `common.mayastor` fixtures.

Risks and test signals: log-string coupling can break on harmless wording changes. CPU thresholds are intentionally broad but still host-sensitive. The tests provide direct signals for interrupt-mode activation, idle sleep behavior, and eventfd wakeup latency.
