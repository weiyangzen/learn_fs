<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2ba.py -->
# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2ba.py

## Purpose

Implements rvgen's LTL parser and on-the-fly Buchi automaton construction. It accepts `RULE = <LTL spec>` plus optional uppercase subexpression assignments, normalizes temporal formulas, expands graph nodes using the Gerth-Peled-Vardi-Wolper algorithm, and returns atoms plus graph nodes for code generation.

## Important APIs, Types, and Functions

Source size: 567 lines, 13509 bytes. Functions/classes: t_error, GraphNode, __init__, expand, __lt__, ASTNode, __init__, __hash__, __eq__, __iter__, negate, expand, __str__, normalize, BinaryOp, __init__, __hash__, __iter__, plus 82 more. Python imports: ply.lex, ply.yacc, .automata.

## Control Flow and Data Flow

PLY lex/yacc tokenizes lowercase temporal operators, uppercase atom names, booleans, parentheses, and assignments. `parse_ltl()` parses assignments, locates `RULE`, substitutes named subexpressions, and returns an AST. `create_graph()` normalizes every reachable AST node, collects atomic variables, expands the initial node set, fixes node ids, links incoming/outgoing edges, and labels non-temporal state predicates.

## State and Persistence Behavior

AST and graph ids are class counters, while each `GraphNode` carries `incoming`, `outgoing`, `new`, `old`, `next`, `labels`, and `init` fields. No persistent files are written; all state is in memory and is consumed by `ltl2k.py`.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

The grammar has limited precedence because binary productions start with `opd`, so ambiguous formulas depend on explicit parentheses. Negation and normalization mutate AST nodes in place, which makes object identity important for contradiction checks. Unsupported lowercase atom names and parser errors surface as `AutomataError` paths.

## Test Signals

Parser tests should cover literals, variables, nested parentheses, every operator, assignment substitution, missing `RULE`, comments, illegal characters, contradictory labels, `next` propagation, and known LTL formulas with expected Buchi graph size/labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/ltl2ba.py -->
