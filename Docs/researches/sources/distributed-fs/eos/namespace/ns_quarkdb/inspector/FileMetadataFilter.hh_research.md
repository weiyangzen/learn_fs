## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.hh

Purpose: Declares file metadata filter abstractions and the expression lexer/parser used by QuarkDB inspector tools.

Important APIs and types: `FileMetadataFilter` is the abstract interface with `isValid()`, `check()`, and `describe()`. `StringEvaluator` represents either a literal string or metadata variable. `EqualityFileMetadataFilter` compares two evaluators. `LogicalMetadataFilter` composes two filters with AND/OR semantics. `TokenType` and `ExpressionLexicalToken` model the expression language. `FilterExpressionLexer::lex()` tokenizes strings; `FilterExpressionParser` parses input and returns a filter plus status.

State and integration: parser/filter objects own their composed subfilters via `unique_ptr`. The interface is designed for inspectors scanning many `FileMdProto` records and applying the same parsed predicate repeatedly.

Dependencies: `FileMdProto`, EOS namespace macros, and `common::Status`.

Risks and test signals: the grammar supported by implementation is narrower than the enum suggests. Callers must check `getStatus()` before using `getFilter()`, and must call `getFilter()` only once. Tests should verify `describe()` stability, validity reporting, parser ownership transfer, and expected grammar documentation.
