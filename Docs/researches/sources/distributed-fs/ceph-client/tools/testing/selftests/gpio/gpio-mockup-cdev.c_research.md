<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-cdev.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-cdev.c

## Purpose
This helper drives GPIO mockup lines through cdev v1 or v2 APIs for the shell tests.

## Important APIs, Types, And Functions
It provides `request_line_v2()`, `get_value_v2()`, `request_line_v1()`, `get_value_v1()`, `usage()`, `wait_signal()`, and `main()`. Options select active-low, bias (`pull-up`, `pull-down`, `disabled`), output value, and uAPI version.

## Control Flow
The helper opens a gpiochip, requests one line as input or output using v1/v2 ioctl structures, closes the chip fd, then either waits for a termination signal while holding an output request or reads and returns the input value as the process exit code.

## State And Persistence
It holds a line request fd while running and can drive output values or request bias configuration. Output state persists while the fd is held and according to GPIO subsystem semantics after close.

## Dependencies And Integration Points
It is used by GPIO mockup, simulator, and aggregator scripts to set/read lines and biases via cdev.

## Risks
Returning the line value as process exit code is intentional but unusual. Bias option strings that do not match known values silently leave bias unchanged. Output mode blocks until signal, so callers must kill it.

## Test Signals
Exit `0` or `1` from input reads maps to line value, while background output processes should change backend mockup/sysfs values and terminate cleanly on signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/gpio-mockup-cdev.c -->
