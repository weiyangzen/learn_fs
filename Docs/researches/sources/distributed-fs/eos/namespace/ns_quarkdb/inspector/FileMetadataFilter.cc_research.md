## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.cc

Purpose: Implements a small expression language for filtering file metadata by string equality/inequality and logical conjunction.

Important APIs and control flow: `StringEvaluator` either returns a literal or delegates a variable to `AttributeExtraction::asString()`. `EqualityFileMetadataFilter` evaluates both sides and compares them, optionally reversed for `!=`. `LogicalMetadataFilter` short-circuits `||` and `&&`, though the parser currently only constructs `&&`. `FilterExpressionLexer::lex()` tokenizes parentheses, single-quoted literals, `==`, `!=`, `&&`, `||`, and alphabetic variable sequences. `FilterExpressionParser` lexes input, then recursively consumes blocks and equality expressions into filter objects.

State behavior: filters are heap-composed through `std::unique_ptr`. Parser state tracks token vector, current index, status, debug flag, and final filter. `getFilter()` transfers ownership and is intended for one call.

Dependencies and integration: consumed by inspector commands to decide whether a `FileMdProto` should be shown. Depends on `AttributeExtraction`, EOS `common::Status`, and assertion/status helpers.

Risks and test signals: lexer recognizes `||`, but `consumeBlock()` only accepts `&&`, leaving OR effectively unsupported unless parenthesized parsing is extended. Variable lexing stops only on whitespace or end, so punctuation like `)` following a variable can be swallowed into the variable token in expressions without spaces. The `|` error message says "single stray '||'". Constructor does not check for trailing tokens after `consumeBlock()`. `isValid()` evaluates variables on an empty proto, which validates attribute names but may perform formatting defaults. Tests should cover lexer errors, missing spaces around parentheses/operators, unsupported OR, trailing garbage, invalid variables, short-circuit behavior, and literal/attribute comparisons.
