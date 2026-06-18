# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/test_ec_policies.xml

Purpose: user-defined erasure coding policy fixture for HDFS tests. It models the expected XML policy format, including a layout version, schema definitions, and policies that combine schema IDs with cell sizes.

Important structure and APIs: top-level `<configuration>` contains `<layoutversion>1</layoutversion>`, `<schemas>`, and `<policies>`. Schemas define `codec`, data units `k`, parity units `m`, and options. Policies reference schemas by ID and set `cellsize` values in bytes.

Control flow: there is no executable flow; parser tests load this file, validate the layout version, build schema objects, then bind policies to schemas. The included schemas cover `xor`, `rs`, `rs-legacy`, and an uppercase `RS` entry marked as intended for failed-test coverage.

State and persistence behavior: read-only fixture with no persistence. The policy parser materializes transient EC schema/policy instances for tests.

Dependencies and integration points: integrates with HDFS erasure coding policy XML parsing and validation. It depends on available codec names and cell-size validation rules, including positive multiples of 1024 and case-insensitive uniqueness comments.

Risks: comment and fixture intent indicate one schema is for negative testing; if codec normalization or accepted codec sets change, this fixture may change behavior. Cell sizes are literal values, so unit interpretation changes would break tests.

Test signals: parser tests can assert valid policy loading for XOR, RS, and RS-LEGACY schemas, while also exercising failure handling for a deliberately questionable uppercase schema entry.
