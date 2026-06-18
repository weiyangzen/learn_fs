# sources/cloud-native/stargz-snapshotter/nativeconverter/nativeconverter.go

Purpose: Empty package anchor for `nativeconverter`; it exists so the package directory passes Go linting even though implementation lives in subpackages.
Important APIs/types/functions: no exported APIs, types, or functions. The only effective declaration is `package nativeconverter`.
Control flow: none.
State and persistence: none.
Dependencies and integration points: establishes the package namespace for tooling and import path stability.
Risks: behavioral risk is negligible; deleting it could break lint or package discovery if the directory otherwise has no Go source.
Test signals: no direct tests required beyond package/lint checks.
