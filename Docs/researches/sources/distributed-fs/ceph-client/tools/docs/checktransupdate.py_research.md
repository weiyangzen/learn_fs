# sources/distributed-fs/ceph-client/tools/docs/checktransupdate.py

Purpose: Checks whether translated documentation files lag behind their original English documentation based on git history.

Important APIs, types, and functions: `get_origin_path()` maps `Documentation/translations/<locale>/...` to the original path. `get_latest_commit_from()` shells out to `git log` and parses hash/author/commit dates/message. `get_origin_from_trans_smartly()` extracts tracked origin hashes from translation commit messages. `get_origin_from_trans()` falls back to author-date walk. `get_commits_count_between()` and `pretty_output()` report pending commits. `list_files_with_excluding_folders()` discovers rst files. `DmesgFormatter` and `config_logging()` configure timestamped logs. `main()` handles locale, logging, missing translations, file/directory inputs.

Control flow: With no files, it scans all non-translation `Documentation/**/*.rst`, maps each to the requested locale, logs missing translations, and checks existing translations. With files/directories, it expands inputs. It converts paths relative to the kernel root, changes cwd to that root, and checks each translation by comparing origin commit tracked by translation vs latest origin HEAD commit.

State and persistence: Writes a log file, default `checktransupdate.log`, in the caller's current directory at configuration time. It does not modify docs.

Dependencies and integration points: Depends on git history, commit message conventions, documentation tree layout, and Python logging. Supports localization maintenance workflows.

Risks: Uses `os.popen()` with formatted file/commit strings and assumes trusted paths. Author-date fallback can be inaccurate across rebases or backports. `valid_locales()` raises literal `"Invalid locale: {locale}"` without interpolation. `config_logging()` ignores the `--logfile` argument because `main()` calls it without passing `args.logfile`.

Test signals: Check one translation file with known tracked commit, directory expansion, default locale scan, missing translation reporting toggles, invalid locale, and log file option behavior.
