# sources/control-plane/mayastor/test/grpc/multi_reporter.js

Purpose: custom Mocha reporter wrapper that fans out events to multiple built-in reporters.

Important APIs/types/functions: `MultiReporter(runner, options)` reads `options.reporterOptions.reporters`, splits it on spaces, looks up each `mocha.reporters[report]`, instantiates it with the same runner/options, stores instances, and `epilogue` calls each child reporter's epilogue.

Control flow: if reporters option is missing or invalid, it prints diagnostics and continues with whatever valid reporters were instantiated.

State/persistence: reporter instances hold Mocha run state and may write reports according to their own options.

Dependencies/integration: used by `grpc-test.sh` to run `xunit` and `spec` reporters in one mocha invocation.

Risks: only proxies `epilogue`; it relies on reporter constructors registering their own runner listeners. Invalid reporter names do not fail the process.

Test signals: a grpc mocha run should emit both console spec output and xunit XML when configured with `reporters="xunit spec"`.
