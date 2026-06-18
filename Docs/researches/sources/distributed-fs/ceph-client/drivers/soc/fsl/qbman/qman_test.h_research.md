# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/qman_test.h

## Purpose
Shared header for QMan test modules. It includes the private QMan implementation header so the tests can use both public APIs and internal portal constants.

## Important APIs, types, and functions
Declares `int qman_test_stash(void);` and `int qman_test_api(void);`. It otherwise relies on `qman_priv.h` for QMan types, frame descriptor helpers, SDQCR/VDQCR constants, and callback enums.

## Control flow and state behavior
The header contains no executable state. Its effect is compile-time coupling of the test sources to private QMan internals.

## Dependencies and integration points
It is included by `qman_test.c`, `qman_test_api.c`, and `qman_test_stash.c`. Because it includes private headers rather than only public interfaces, the tests can validate lower-level behavior but also track internal layout changes closely.

## Risks and test signals
The main risk is overcoupling tests to private implementation details. Any private header refactor can break test builds even if the public API remains stable. Successful compilation and module load validate that the private test contract still matches the QMan implementation.
