# sources/control-plane/rook/.docs/macros/includes/main.py

Purpose: MkDocs macro helper that rewrites Rook GitHub links from `master` to the currently checked-out branch/tag.

Important APIs and control flow: module-level regex matches `github.com/.../rook/.../master/` links and a substitution template inserts the target ref. `define_env(env)` opens the current repository with `pygit2.Repository(".")`, reads `repo.head.shorthand`, and stores it in `env.variables["current_branch"]`. `on_post_page_macros(env)` skips rewriting on `master`; otherwise it runs `re.sub` over `env.markdown`.

State, dependencies, and integration: state is the macro environment variable `current_branch` and modified page markdown. It depends on pygit2, regex, MkDocs macros lifecycle hooks, and being executed from a Git worktree.

Risks and test signals: detached HEADs or nonstandard execution directories can produce unsuitable branch names or repository errors. The regex is broad and rewrites all matching markdown after macro expansion. Signals are rendered documentation links pointing at the active branch rather than master.
