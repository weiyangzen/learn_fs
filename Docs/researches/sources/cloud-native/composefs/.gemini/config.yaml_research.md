# sources/cloud-native/composefs/.gemini/config.yaml

Purpose: Gemini code-review automation configuration, maintained from bootc-dev infra common config.

Important APIs/types/functions: `have_fun`, `code_review.disable=false`, severity threshold `MEDIUM`, unlimited max review comments, PR-opened help/summary disabled, code review enabled, and empty ignore patterns.

Control flow: Gemini reads this during PR review to decide comment behavior.

State/persistence: automation configuration only.

Dependencies/integration: depends on Gemini review tooling and shared infra maintenance.

Risks/test signals: comment volume can be high with unlimited comments; "DO NOT EDIT" means local changes may be overwritten.
