<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.l -->
# sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.l

Purpose: this flex lexer tokenizes the low-level classic BPF assembly language used by `bpf_asm`.

Important APIs/tokens: it recognizes instruction mnemonics such as `ldb`, `ldh`, `ld`, `ldi`, `ldx`, `ldxi`, `ldxb`, `st`, `stx`, jump operations, ALU operations, `ret`, `tax`, and `txa`. It maps extension aliases such as `proto`, `type`, `poff`, `ifidx`, `nla`, `mark`, `queue`, `cpu`, VLAN fields, and `rand` to `SKF_AD_*` numbers. It returns punctuation tokens, `number`, `label`, `extension`, and `K_PKT_LEN` to the bison parser.

Control flow: flex rules are case-insensitive and skip C comments, semicolon comments, preprocessor-style line comments, spaces, tabs, and newlines. Numeric literals support hex, binary, signed/unsigned decimal, and octal. Labels are duplicated with `strdup()` and later freed by the parser's label cleanup.

State and persistence: lexer state is generated flex state. `yylval` carries labels and numbers. No persistent files are written.

Dependencies and integration points: it includes `linux/filter.h` and the generated `bpf_exp.yacc.h` token definitions. Its token choices are tightly coupled to grammar productions in `bpf_exp.y`.

Risks: label regex requires at least two characters because it uses `[a-zA-Z_][a-zA-Z0-9_]+`, so one-character labels are not accepted. Unknown characters call `yyerror()` after printing a message without a newline. Numeric conversion does not check overflow. `strdup()` failure is not handled before returning a label token.

Test signals: lexer/parser tests should cover every mnemonic, extension alias with and without `#`, numeric base, comments, whitespace, labels, single-character label rejection, unknown characters, and case-insensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bpf/bpf_exp.l -->
