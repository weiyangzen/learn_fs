# sources/distributed-fs/ceph-client/drivers/remoteproc/qcom_wcnss.h

Purpose: declares the small private interface between the WCNSS remoteproc driver and the IRIS RF child helper.

Important APIs/types/functions: `struct wcnss_vreg_info` describes regulator name, voltage range, load, and a `super_turbo` flag used in WCNSS/IRIS regulator tables. The header forward-declares `struct qcom_iris` and `struct qcom_wcnss`, and declares `qcom_iris_probe()`, `qcom_iris_remove()`, `qcom_iris_enable()`, and `qcom_iris_disable()`.

Control flow: there is no executable logic. `qcom_wcnss.c` calls `qcom_iris_probe()` during probe to create and configure the child, `qcom_iris_enable()` before WCNSS PAS auth, `qcom_iris_disable()` after boot or on failures, and `qcom_iris_remove()` during remove.

State and persistence: the header defines compile-time contracts only. Runtime IRIS state is owned by `qcom_wcnss_iris.c`; regulator table constants are provided by including C files and are not persistent.

Dependencies and integration: depends on the including files for basic kernel types such as `struct device` and `bool`. It is local to `drivers/remoteproc` and not exported as userspace API.

Risks and test signals: the `super_turbo` field is present in the shared regulator description but not acted on by the viewed IRIS/WCNSS code, so platform assumptions should be checked. Compile coverage should ensure the header is included only where kernel device/bool declarations are already visible or indirectly provided.
