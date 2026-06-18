# sources/cloud-native/cri-o/internal/config/ulimits/ulimits_test.go

Purpose: validates basic ulimits config construction and parsing.

Important APIs/types/functions: `ulimits.New`, `LoadUlimits`, and `Ulimits`.

Control flow: tests assert a new config has no limits, invalid `hi=-1:-1` returns an error and leaves limits empty, and valid `locks=10:64` succeeds and stores at least one limit.

State and persistence behavior: in-memory only.

Dependencies/integration points: Ginkgo/Gomega and the ulimits package.

Risks: does not assert exact normalized `RLIMIT_` names or hard/soft numeric values, and does not cover repeated loads.

Test signals: focused smoke coverage for parse success/failure.
