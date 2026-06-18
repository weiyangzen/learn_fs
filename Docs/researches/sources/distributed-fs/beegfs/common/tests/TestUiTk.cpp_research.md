# sources/distributed-fs/beegfs/common/tests/TestUiTk.cpp

Purpose: This test verifies yes/no prompt parsing in `uitk::userYNQuestion()`.

Important APIs/types/functions: `testQuestion()` wraps a `std::stringstream` around an answer string and passes it, plus an optional default answer, to `uitk::userYNQuestion("Test", defaultAnswer, input)`.

Control flow: The test asserts affirmative parsing for `Y`, `y`, and `Yes`; negative parsing for `N`, `n`, and `No`; default behavior for empty input with true and false defaults; and explicit answers overriding defaults.

State and persistence behavior: No persistent state exists. Input is supplied through an in-memory stream, making the test deterministic and independent of terminal state.

Dependencies and integration: This helper is relevant to setup or administrative tools that ask interactive confirmation questions. Correct defaults are important because empty input can imply destructive or enabling actions.

Risks and test signals: The test covers common English responses but not whitespace, invalid retries, EOF handling, localized strings, multi-character mixed-case variants beyond `Yes`/`No`, or prompt output formatting.
