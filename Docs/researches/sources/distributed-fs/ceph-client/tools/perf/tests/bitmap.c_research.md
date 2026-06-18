# sources/distributed-fs/ceph-client/tools/perf/tests/bitmap.c

Purpose: `bitmap.c` tests bitmap string formatting used by perf utilities.

Important APIs and state: the file builds small static bitmap cases, formats them through perf's bitmap printing helper, and compares the resulting string with expected compact range/list syntax. The suite is registered as `"Print bitmap"`.

Control flow: the test populates bitmap words with selected bits, calls the formatting helper into a fixed buffer, and asserts the printed representation matches expected output. It covers empty/single/range/list style behavior rather than runtime perf events.

State and persistence: all state is stack-local test data; no file or kernel state is touched.

Dependencies, integration, risks, and tests: it depends on perf's bitmap helper and Linux bitmap primitives. Risks are mostly buffer-size assumptions and formatting contract churn. Test signals are exact string comparisons for representative bit patterns.
