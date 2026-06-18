## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-junit-reports.sh

Purpose: combines per-sharness JUnit XML result files into a single aggregate XML report.

Important control flow: the script scans sharness `test-results` XML files, wraps or concatenates their testcase/testsuite content into `test-results/sharness.xml`, and is invoked from `Rules.mk` after test targets. State is the aggregate XML report under `test/sharness/test-results`.

Dependencies and integration points: depends on sharness running with JUnit output (`TEST_JUNIT=1`) and common shell/XML text utilities. CI systems consume the resulting XML.

Risks: XML aggregation via shell text processing can be brittle if sharness output format changes or filenames contain unexpected characters. Test signal is a non-empty aggregate JUnit report with all executed tests represented.
