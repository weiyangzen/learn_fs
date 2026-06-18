# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_chmod_non_octal_test.go

Purpose: integration-tests symbolic, non-octal `COPY --chmod` behavior.

Important test cases: file and directory copies with modes `go-w`, `u=rw,g=r,o=r`, `a+X`, and compound symbolic forms. Windows is skipped.

Control flow and state: builds a Dockerfile that creates base input files/dirs, independently computes expected permissions with shell `chmod`, copies using `COPY --chmod` into a scratch result stage, then compares `stat -c %A` between actual and expected in a final stage.

Dependencies and integration: exercises `convert_copy.go` symbolic mode parsing through `dchapes-mode`, LLB copy chmod handling, multi-stage COPY, and frontend integration sandbox.

Risks and test signals: protects symbolic chmod compatibility and directory execute-bit behavior. It does not cover invalid symbolic expressions; parser/unit tests should cover failures.
