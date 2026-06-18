# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/tlmm-test.c

## Purpose
This file is a KUnit-based hardware-oriented test module for Qualcomm TLMM interrupt behavior. It validates that the common TLMM/pinctrl-msm driver delivers the expected number of interrupts when an otherwise unused, non-connected GPIO pin is driven by changing the TLMM pull configuration directly in MMIO. It currently allow-lists `qcom,sc8280xp-tlmm` and `qcom,x1e80100-tlmm`.

## Important APIs, Types, and Functions
- Module parameters `gpio` and `name` select the GPIO number under test and the TLMM register region name. `gpio` is mandatory.
- `tlmm_suite` stores shared suite state: mapped TLMM base, selected GPIO config register, mapped IRQ, and precomputed pull-down/pull-up register values.
- `struct tlmm_test_priv` stores per-test atomic interrupt counters and operation masks for hard IRQ and threaded IRQ handlers.
- Operation flags include `TLMM_TEST_COUNT`, `TLMM_TEST_OUTPUT_LOW`, `TLMM_TEST_OUTPUT_HIGH`, `TLMM_TEST_THEN_HIGH`, `TLMM_TEST_THEN_LOW`, and `TLMM_TEST_WAKE_THREAD`.
- `tlmm_output_low()` and `tlmm_output_high()` directly write pull-down or pull-up values to the selected TLMM GPIO register and read back to flush.
- `tlmm_test_intr_fn()` and `tlmm_test_intr_thread_fn()` implement configurable hard and threaded handler behavior.
- `tlmm_test_request_hard_irq()` and `tlmm_test_request_threaded_irq()` request the mapped IRQ for each test.
- Test cases cover silent lines, rising/falling edges, high/low level interrupts, retriggering from the hard handler, threaded IRQ delivery, retriggering from threaded handlers, and edge delivery while disabled.
- `tlmm_reg_base()` chooses the MMIO resource from `reg-names` and `name` parameter.
- `tlmm_test_init_suite()` discovers the TLMM node, maps registers, creates an IRQ mapping, and computes register values.
- `kunit_test_suites()` registers the test suite.

## Control Flow
Suite initialization requires `tlmm-test.gpio` to be set. It finds a matching TLMM node, resolves the requested register resource, maps it with `ioremap()`, creates an IRQ mapping using a two-cell OF phandle argument with the selected GPIO and flags 0, selects the pin's MMIO register as `base + gpio * TLMM_REG_SIZE`, and computes low/high pull values by preserving all bits except the pull mask.

Each test allocates a fresh `tlmm_test_priv`, configures handler operation masks, sets the initial pin level by writing pull state, requests a hard or threaded IRQ with a trigger mode, generates transitions through direct MMIO writes and sleeps, frees the IRQ, and asserts exact interrupt counts. Handler-driven tests simulate retriggering by changing pull state in the interrupt handler after short delays.

Suite exit disposes the IRQ mapping and unmaps TLMM MMIO.

## State and Persistence
Shared suite state persists for the whole KUnit suite in `tlmm_suite`. Per-test counters and operations are allocated with KUnit-managed memory and reset for each test. The test intentionally modifies live TLMM pull configuration for the selected GPIO and does not restore the original pull value at suite exit beyond preserving unrelated bits when computing low/high values.

## Dependencies and Integration Points
The test depends on KUnit, OF address/IRQ helpers, direct MMIO access, Linux IRQ APIs, and a real TLMM node with compatible in `tlmm_of_match`. It assumes TLMM register layout uses `TLMM_REG_SIZE` spacing and pull values `MSM_PULL_DOWN`/`MSM_PULL_UP`. It integrates with the same X1E80100 TLMM descriptor researched in this subset and with the common `pinctrl-msm` IRQ handling.

## Risks and Edge Cases
- This is not a pure unit test; it requires real hardware or an equivalent environment, a safe unused non-connected GPIO, and correct module parameters.
- The source snapshot contains an extra `}` in `tlmm_test_falling()`, which would break compilation.
- Direct MMIO writes bypass pinctrl/gpiolib locking and state tracking, so tests can interfere with active board functions if the chosen GPIO is wrong.
- Timing uses `msleep()` and `udelay()` with exact interrupt counts; marginal hardware or scheduler delays may cause flaky results.
- Suite initialization requires `reg-names`; TLMM nodes lacking that property fail even when resource 0 would otherwise be usable.
- The original pin pull state is not restored after tests.

## Test Signals
The file itself is the test signal for TLMM interrupt behavior. Passing KUnit cases indicate correct edge/level interrupt handling, hard/threaded delivery, retrigger behavior, and disabled-then-enabled edge delivery for the chosen GPIO. Build tests with `CONFIG_KUNIT` and the target TLMM driver are also necessary because the source snapshot has a visible syntax-risk marker.
